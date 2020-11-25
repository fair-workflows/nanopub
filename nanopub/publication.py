from datetime import datetime
from typing import Union
from urllib.parse import urldefrag

import rdflib
from rdflib.namespace import RDF, DC, DCTERMS, XSD

from nanopub import namespaces, profile
from nanopub.definitions import DUMMY_NANOPUB_URI


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

    @staticmethod
    def _replace_blank_nodes(dummy_namespace, rdf):
        """ Replace blank nodes.

        Replace any blank nodes in the supplied RDF with a corresponding uri in the
        dummy_namespace.'Blank nodes' here refers specifically to rdflib.term.BNode objects. When
        publishing, the dummy_namespace is replaced with the URI of the actual nanopublication.

        For example, if the nanopub's URI is www.purl.org/ABC123 then the blank node will be
        replaced with a concrete URIRef of the form www.purl.org/ABC123#blanknodename where
        'blanknodename' is the name of the rdflib.term.BNode object.

        This is to solve the problem that a user may wish to use the nanopublication to introduce
        a new concept. This new concept needs its own URI (it cannot simply be given the
        nanopublication's URI), but it should still lie within the space of the nanopub.
        Furthermore, the URI the nanopub is published to is not known ahead of time.
        """
        for s, p, o in rdf:
            rdf.remove((s, p, o))
            if isinstance(s, rdflib.term.BNode):
                s = dummy_namespace[str(s)]
            if isinstance(o, rdflib.term.BNode):
                o = dummy_namespace[str(o)]
            rdf.add((s, p, o))

    @classmethod
    def from_assertion(cls, assertion_rdf: rdflib.Graph,
                       introduces_concept: rdflib.term.BNode = None,
                       derived_from=None, assertion_attributed_to=None,
                       attribute_assertion_to_profile: bool = False,
                       provenance_rdf: rdflib.Graph = None,
                       pubinfo_rdf: rdflib.Graph = None
                       ):
        """
        Construct Nanopub object based on given assertion. Any blank nodes in the rdf graph are
        replaced with the nanopub's URI, with the blank node name as a fragment. For example, if
        the blank node is called 'step', that would result in a URI composed of the nanopub's (base)
        URI, followed by #step.

        Args:
            assertion_rdf: The assertion RDF graph.
            introduces_concept: the pubinfo graph will note that this nanopub npx:introduces the
                concept. The concept should be a blank node (rdflib.term.BNode), and is converted
                to a URI derived from the nanopub's URI with a fragment (#) made from the blank
                node's name.
            derived_from: Add a triple to the provenance graph stating that this nanopub's assertion prov:wasDerivedFrom the given URI.
                          If a list of URIs is passed, a provenance triple will be generated for each.
            assertion_attributed_to: the provenance graph will note that this nanopub's assertion
                prov:wasAttributedTo the given URI.
            attribute_assertion_to_profile: Attribute the assertion to the ORCID iD in the profile
            provenance_rdf: RDF triples to be added to provenance graph of the nanopublication.
                This is optional, for most cases the defaults will be sufficient.
            pubinfo_rdf: RDF triples to be added to the publication info graph of the
                nanopublication. This is optional, for most cases the defaults will be sufficient.
        """
        if assertion_attributed_to and attribute_assertion_to_profile:
            raise ValueError(
                'If you pass a URI for the assertion_attributed_to argument, you cannot pass '
                'attribute_assertion_to_profile=True, because the assertion will already be '
                'attributed to the value passed in assertion_attributed_to argument. Set '
                'attribute_assertion_to_profile=False or do not pass the assertion_attributed_to '
                'argument.')
        if attribute_assertion_to_profile:
            assertion_attributed_to = rdflib.URIRef(profile.get_orcid_id())

        if introduces_concept and not isinstance(introduces_concept, rdflib.term.BNode):
            raise ValueError('If you want a nanopublication to introduce a concept, you need to '
                             'pass it as an rdflib.term.BNode("concept_name"). This will make '
                             'sure it is referred to from the nanopublication uri namespace upon '
                             'publishing.')

        if provenance_rdf:
            if derived_from and (None, namespaces.PROV.wasDerivedFrom, None) in provenance_rdf:
                raise ValueError('The provenance_rdf that you passed already contains the '
                                 'prov:wasDerivedFrom predicate, so you can not also use the '
                                 'derived_from argument')
            if assertion_attributed_to and (None, namespaces.PROV.wasAttributedTo, None) in provenance_rdf:
                raise ValueError('The provenance_rdf that you passed already contains the '
                                 'prov:wasAttributedTo predicate, so you can not also use the '
                                 'assertion_attributed_to argument')
            if attribute_assertion_to_profile and (None, namespaces.PROV.wasAttributedTo, None) in provenance_rdf:
                raise ValueError('The provenance_rdf that you passed already contains the '
                                 'prov:wasAttributedTo predicate, so you can not also use the '
                                 'attribute_assertion_to_profile argument')
        if pubinfo_rdf:
            if introduces_concept and (None, namespaces.NPX.introduces, None) in pubinfo_rdf:
                raise ValueError('The pubinfo_rdf that you passed already contains the '
                                 'npx:introduces predicate, so you can not also use the '
                                 'introduces_concept argument')

        # To be replaced with the published uri upon publishing
        this_np = rdflib.Namespace(DUMMY_NANOPUB_URI + '#')

        # Set up different contexts
        main_graph = rdflib.ConjunctiveGraph()
        head = rdflib.Graph(main_graph.store, this_np.Head)
        assertion = rdflib.Graph(main_graph.store, this_np.assertion)
        provenance = rdflib.Graph(main_graph.store, this_np.provenance)
        pubinfo = rdflib.Graph(main_graph.store, this_np.pubInfo)

        main_graph.bind("", this_np)
        main_graph.bind("np", namespaces.NP)
        main_graph.bind("npx", namespaces.NPX)
        main_graph.bind("prov", namespaces.PROV)
        main_graph.bind("hycl", namespaces.HYCL)
        main_graph.bind("dc", DC)
        main_graph.bind("dcterms", DCTERMS)

        head.add((this_np[''], RDF.type, namespaces.NP.Nanopublication))
        head.add((this_np[''], namespaces.NP.hasAssertion, this_np.assertion))
        head.add((this_np[''], namespaces.NP.hasProvenance, this_np.provenance))
        head.add((this_np[''], namespaces.NP.hasPublicationInfo, this_np.pubInfo))

        for user_rdf in [assertion_rdf, provenance_rdf, pubinfo_rdf]:
            if user_rdf is not None:
                for prefix, namespace in user_rdf.namespaces():
                    main_graph.bind(prefix, namespace)
                cls._replace_blank_nodes(dummy_namespace=this_np, rdf=user_rdf)
        assertion += assertion_rdf
        if provenance_rdf is not None:
            provenance += provenance_rdf
        if pubinfo_rdf is not None:
            pubinfo += pubinfo_rdf

        creationtime = rdflib.Literal(datetime.now(), datatype=XSD.dateTime)
        provenance.add((this_np.assertion, namespaces.PROV.generatedAtTime, creationtime))

        pubinfo.add((this_np[''], namespaces.PROV.generatedAtTime, creationtime))

        if assertion_attributed_to:
            assertion_attributed_to = rdflib.URIRef(assertion_attributed_to)
            provenance.add((this_np.assertion,
                            namespaces.PROV.wasAttributedTo,
                            assertion_attributed_to))

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

        # Always attribute the nanopublication (not the assertion) to the ORCID iD in user profile
        pubinfo.add((this_np[''],
                      namespaces.PROV.wasAttributedTo,
                      rdflib.URIRef(profile.get_orcid_id())))

        if introduces_concept:
            # Convert introduces_concept URI to an rdflib term first (if necessary)
            if isinstance(introduces_concept, rdflib.term.BNode):
                introduces_concept = this_np[str(introduces_concept)]
            else:
                introduces_concept = rdflib.URIRef(introduces_concept)

            pubinfo.add((this_np[''],
                          namespaces.NPX.introduces,
                          introduces_concept))

        return cls(rdf=main_graph)

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


def replace_in_rdf(rdf: rdflib.Graph, oldvalue, newvalue):
    """
    Replace subjects or objects of oldvalue with newvalue
    """
    for s, p, o in rdf:
        if s == oldvalue:
            rdf.remove((s, p, o))
            rdf.add((newvalue, p, o))
        elif o == oldvalue:
            rdf.remove((s, p, o))
            rdf.add((s, p, newvalue))
