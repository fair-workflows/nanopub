from datetime import datetime
from urllib.parse import urldefrag

import rdflib
from rdflib.namespace import RDF, DC, DCTERMS, XSD

from nanopub import namespaces, profile
from nanopub.definitions import DEFAULT_NANOPUB_URI


class Publication:
    """
    Representation of the rdf that comprises a nanopublication
    """

    def __init__(self, rdf=None, source_uri=None):
        self._rdf = rdf
        self._source_uri = source_uri

        # Extract the Head, pubinfo, provenance and assertion graphs from the assigned nanopub rdf
        self._graphs = {}
        for c in rdf.contexts():
            graphid = urldefrag(c.identifier).fragment.lower()
            self._graphs[graphid] = c

        # Check all four expected graphs are provided
        expected_graphs = ['head', 'pubinfo', 'provenance', 'assertion']
        for expected in expected_graphs:
            if expected not in self._graphs.keys():
                raise ValueError(
                    f'Expected to find {expected} graph in nanopub rdf, but not found. Graphs found: {list(self._graphs.keys())}.')

    @classmethod
    def from_assertion(cls, assertion_rdf, uri=DEFAULT_NANOPUB_URI, introduces_concept=None,
                       derived_from=None, attributed_to=None,
                       attribute_to_profile: bool = False, nanopub_author=None):
        """
        Construct Nanopub object based on given assertion, with given assertion and (defrag'd) URI.
        Any blank nodes in the rdf graph are replaced with the nanopub's URI, with the blank node name
        as a fragment. For example, if the blank node is called 'step', that would result in a URI composed of the
        nanopub's (base) URI, followed by #step.

        If introduces_concept is given (string, or rdflib.URIRef), the pubinfo graph will note that this nanopub npx:introduces the given URI.
        If a blank node (rdflib.term.BNode) is given instead of a URI, the blank node will be converted to a URI
        derived from the nanopub's URI with a fragment (#) made from the blank node's name.

        Args:
            derived_from: Add that this nanopub prov:wasDerivedFrom the given URI to the provenance graph.
                          If a list of URIs is passed, a provenance triple will be generated for each.
            attributed_to: the provenance graph will note that this nanopub prov:wasAttributedTo
                the given URI.
            attribute_to_profile: Attribute the nanopub to the ORCID iD in the profile
            nanopub_author: the pubinfo graph will note that this nanopub prov:wasAttributedTo the
                given URI. If no nanopub_author is provided we default to the author from the
                profile

        """

        if nanopub_author is None and profile.get_orcid_id() is not None:
            nanopub_author = rdflib.URIRef(profile.get_orcid_id())

        if attributed_to and attribute_to_profile:
            raise ValueError('If you pass a URI for the attributed_to argument, you cannot pass '
                             'attribute_to_profile=True, because the nanopub will already be '
                             'attributed to the value passed in attributed_to argument. Set '
                             'attribute_to_profile=False or do not pass the attributed_to '
                             'argument.')
        if attribute_to_profile and profile.get_orcid_id() is not None:
            attributed_to = rdflib.URIRef(profile.get_orcid_id())

        # Make sure passed URI is defrag'd
        uri = str(uri)
        uri, _ = urldefrag(uri)
        this_np = rdflib.Namespace(uri + '#')

        # Replace any blank nodes in the supplied RDF, with a URI derived from the nanopub's uri.
        # 'Blank nodes' here refers specifically to rdflib.term.BNode objects.
        # For example, if the nanopub's URI is www.purl.org/ABC123 then the blank node will be replaced with a
        # concrete URIRef of the form www.purl.org/ABC123#blanknodename where 'blanknodename' is the name of the
        # the rdflib.term.BNode object. If blanknodename is 'step', then the URI will have a fragment '#step' after it.
        #
        # The problem that this is designed to solve is that a user may wish to use the nanopublication to introduce
        # a new concept. This new concept needs its own URI (it cannot simply be given the nanopublication's URI),
        # but it should still lie within the space of the nanopub. Furthermore, the URI the nanopub is published
        # is not known ahead of time. The variable 'this_np', for example, is holding a dummy URI that is swapped
        # with the true, published URI of the nanopub by the 'np' tool at the moment of publication.
        #
        # We wish to replace any blank nodes in the rdf with URIs that are based on this same dummy URI, so that
        # they too are transformed to the correct URI upon publishing.
        for s, p, o in assertion_rdf:
            assertion_rdf.remove((s, p, o))
            if isinstance(s, rdflib.term.BNode):
                s = this_np[str(s)]
            if isinstance(o, rdflib.term.BNode):
                o = this_np[str(o)]
            assertion_rdf.add((s, p, o))

        # Set up different contexts
        rdf = rdflib.ConjunctiveGraph()
        # Use namespaces from assertion_rdf
        for prefix, namespace in assertion_rdf.namespaces():
            rdf.bind(prefix, namespace)
        head = rdflib.Graph(rdf.store, this_np.Head)
        assertion = rdflib.Graph(rdf.store, this_np.assertion)
        provenance = rdflib.Graph(rdf.store, this_np.provenance)
        pub_info = rdflib.Graph(rdf.store, this_np.pubInfo)

        rdf.bind("", this_np)
        rdf.bind("np", namespaces.NP)
        rdf.bind("npx", namespaces.NPX)
        rdf.bind("prov", namespaces.PROV)
        rdf.bind("hycl", namespaces.HYCL)
        rdf.bind("dc", DC)
        rdf.bind("dcterms", DCTERMS)

        head.add((this_np[''], RDF.type, namespaces.NP.Nanopublication))
        head.add((this_np[''], namespaces.NP.hasAssertion, this_np.assertion))
        head.add((this_np[''], namespaces.NP.hasProvenance, this_np.provenance))
        head.add((this_np[''], namespaces.NP.hasPublicationInfo,
                  this_np.pubInfo))

        assertion += assertion_rdf

        creationtime = rdflib.Literal(datetime.now(), datatype=XSD.dateTime)
        provenance.add((this_np.assertion, namespaces.PROV.generatedAtTime, creationtime))

        pub_info.add((this_np[''], namespaces.PROV.generatedAtTime, creationtime))

        if attributed_to:
            attributed_to = rdflib.URIRef(attributed_to)
            provenance.add((this_np.assertion,
                            namespaces.PROV.wasAttributedTo,
                            attributed_to))

        if derived_from:
            uris = []
            if isinstance(derived_from, list):
                list_of_URIs = derived_from
            else:
                list_of_URIs = [derived_from]

            for derived_from_uri in list_of_URIs:
                # Convert uri to an rdflib term first (if necessary)
                derived_from_uri = rdflib.URIRef(derived_from_uri)

                provenance.add((this_np.assertion,
                                namespaces.PROV.wasDerivedFrom,
                                derived_from_uri))

        if nanopub_author:
            nanopub_author = rdflib.URIRef(nanopub_author)
            pub_info.add((this_np[''],
                          namespaces.PROV.wasAttributedTo,
                          nanopub_author))

        if introduces_concept:
            # Convert introduces_concept URI to an rdflib term first (if necessary)
            if isinstance(introduces_concept, rdflib.term.BNode):
                introduces_concept = this_np[str(introduces_concept)]
            else:
                introduces_concept = rdflib.URIRef(introduces_concept)

            pub_info.add((this_np[''],
                          namespaces.NPX.introduces,
                          introduces_concept))

        obj = cls(rdf=rdf, source_uri=uri)
        return obj

    @property
    def rdf(self):
        return self._rdf

    @property
    def assertion(self):
        return self._graphs['assertion']

    @property
    def pubinfo(self):
        return self._graphs['pubinfo']

    @property
    def provenance(self):
        return self._graphs['provenance']

    @property
    def source_uri(self):
        return self._source_uri

    @property
    def introduces_concept(self):
        concepts_introduced = list()
        for s, p, o in self.pubinfo.triples((None, namespaces.NPX.introduces, None)):
            concepts_introduced.append(o)

        if len(concepts_introduced) == 0:
            return None
        elif len(concepts_introduced) == 1:
            return concepts_introduced[0]
        else:
            raise ValueError('Nanopub introduces multiple concepts')

    def __str__(self):
        s = f'Original source URI = {self._source_uri}\n'
        s += self._rdf.serialize(format='trig').decode('utf-8')
        return s
