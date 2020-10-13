import os
import tempfile
from datetime import datetime
from enum import Enum, unique
from urllib.parse import urldefrag

import rdflib
import requests
from rdflib.namespace import RDF, DC, DCTERMS, XSD

from nanopub import java_wrapper, namespaces

DEFAULT_URI = 'http://purl.org/nanopub/temp/mynanopub'


class Nanopub:
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

        self._introduces_concept = None

    @classmethod
    def from_assertion(cls, assertion_rdf, uri=DEFAULT_URI, introduces_concept=None,
                       derived_from=None,
                       attributed_to=None, nanopub_author=None):
        """
        Construct Nanopub object based on given assertion, with given assertion and (defrag'd) URI.
        Any blank nodes in the rdf graph are replaced with the nanopub's URI, with the blank node name
        as a fragment. For example, if the blank node is called 'step', that would result in a URI composed of the
        nanopub's (base) URI, followed by #step.

        If introduces_concept is given (string, or rdflib.URIRef), the pubinfo graph will note that this nanopub npx:introduces the given URI.
        If a blank node (rdflib.term.BNode) is given instead of a URI, the blank node will be converted to a URI
        derived from the nanopub's URI with a fragment (#) made from the blank node's name.

        If derived_from is given (string or rdflib.URIRef), the provenance graph will note that this nanopub prov:wasDerivedFrom the given URI.

        If attributed_to is given (string or rdflib.URIRef), the provenance graph will note that this nanopub prov:wasAttributedTo the given URI.

        if nanopub_author is given (string or rdflib.URIRef), the pubinfo graph will note that this nanopub prov:wasAttributedTo the given URI.

        """

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
        head = rdflib.Graph(rdf.store, this_np.Head)
        assertion = rdflib.Graph(rdf.store, this_np.assertion)
        provenance = rdflib.Graph(rdf.store, this_np.provenance)
        pub_info = rdflib.Graph(rdf.store, this_np.pubInfo)

        rdf.bind("", this_np)
        rdf.bind("np", namespaces.NP)
        rdf.bind("npx", namespaces.NPX)
        rdf.bind("p-plan", namespaces.PPLAN)
        rdf.bind("prov", namespaces.PROV)
        rdf.bind("dul", namespaces.DUL)
        rdf.bind("bpmn", namespaces.BPMN)
        rdf.bind("pwo", namespaces.PWO)
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
            # Convert derived_from URI to an rdflib term first (if necessary)
            derived_from = rdflib.URIRef(derived_from)

            provenance.add((this_np.assertion,
                            namespaces.PROV.wasDerivedFrom,
                            derived_from))

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
        obj._introduces_concept = introduces_concept
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
        # TODO: This should eventually look at the pubinfo graph for the
        #  NPX.introduces predicate.
        return self._introduces_concept

    def __str__(self):
        s = f'Original source URI = {self._source_uri}\n'
        s += self._rdf.serialize(format='trig').decode('utf-8')
        return s


@unique
class Formats(Enum):
    """
    Enums to specify the format of nanopub desired
    """
    TRIG = 'trig'


class NanopubClient:
    """
    Provides utility functions for searching, creating and publishing RDF graphs
    as assertions in a nanopublication.
    """

    def search_text(self, searchtext, max_num_results=1000,
                    apiurl='http://grlc.nanopubs.lod.labs.vu.nl//api/local/local/find_nanopubs_with_text'):
        """
        Searches the nanopub servers (at the specified grlc API) for any nanopubs matching the given search text,
        up to max_num_results.
        """

        if len(searchtext) == 0:
            return []

        searchparams = {'text': searchtext, 'graphpred': '', 'month': '', 'day': '', 'year': ''}

        return self._search(searchparams=searchparams,
                            max_num_results=max_num_results,
                            apiurl=apiurl)

    def search_pattern(self, subj=None, pred=None, obj=None,
                       max_num_results=1000, apiurl='http://grlc.nanopubs.lod.labs.vu.nl//api/local/local/find_nanopubs_with_pattern'):
        """
        Searches the nanopub servers (at the specified grlc API) for any nanopubs matching the given RDF pattern,
        up to max_num_results.
        """

        searchparams = {}
        if subj:
            searchparams['subj'] = subj
        if pred:
            searchparams['pred'] = pred
        if obj:
            searchparams['obj'] = obj

        return self._search(searchparams=searchparams,
                            max_num_results=max_num_results, apiurl=apiurl)

    def search_things(self, thing_type=None, searchterm=' ',
                      max_num_results=1000, apiurl='http://grlc.nanopubs.lod.labs.vu.nl/api/local/local/find_things'):
        """
        Searches the nanopub servers (at the specified grlc API) for any nanopubs of the given type, with given search term,
        up to max_num_results.
        """

        searchparams = {}
        if not thing_type or not searchterm:
            print(f"Received thing_type='{thing_type}', searchterm='{searchterm}'")
            raise ValueError('thing_type and searchterm must BOTH be specified in calls to Nanopub.search_things')

        searchparams['type'] = thing_type
        searchparams['searchterm'] = searchterm

        return self._search(searchparams=searchparams,
                            max_num_results=max_num_results, apiurl=apiurl)

    @staticmethod
    def _search(searchparams=None, max_num_results=None, apiurl=None):
        """
        General nanopub server search method. User should use e.g. search_text() or search_pattern() instead.
        """

        if apiurl is None:
            raise ValueError('kwarg "apiurl" must be specified. Consider using search_text() function instead.')

        if max_num_results is None:
            raise ValueError('kwarg "max_num_results" must be specified. Consider using search_text() function instead.')

        if searchparams is None:
            raise ValueError('kwarg "searchparams" must be specified. Consider using search_text() function instead.')


        # Query the nanopub server for the specified text
        headers = {"Accept": "application/json"}
        r = requests.get(apiurl, params=searchparams, headers=headers)

        if r.ok:

            # Make sure that results are provided
            try:
                results_json = r.json()
            except:
                # If the returned message can't be serialized as JSON (such as due to virtuoso error) then there are no results
                print('Error: Could not serialize response as JSON:\n', r.content)
                return []

            results_list = results_json['results']['bindings']
            nanopubs = []

            for result in results_list:
                nanopub = {}
                nanopub['np'] = result['np']['value']

                if 'v' in result:
                    nanopub['description'] = result['v']['value']
                elif 'description' in result:
                    nanopub['description'] = result['description']['value']
                else:
                    nanopub['v'] = ''

                nanopub['date'] = result['date']['value']

                nanopubs.append(nanopub)

                if len(nanopubs) >= max_num_results:
                    break

            return nanopubs

        else:
            return[{'Error': f'Error when searching {apiurl}: Status code {r.status_code}'}]

    @staticmethod
    def fetch(uri, format: str = 'trig'):
        """
        Download the nanopublication at the specified URI (in specified format).

        Returns:
            a Nanopub object.
        """

        if format == Formats.TRIG.value:
            extension = '.trig'
        else:
            raise ValueError(f'Format not supported: {format}, choose from '
                             f'{[format.value for format in Formats]})')

        r = requests.get(uri + extension)
        r.raise_for_status()

        if r.ok:
            nanopub_rdf = rdflib.ConjunctiveGraph()
            nanopub_rdf.parse(data=r.text, format=format)
            return Nanopub(rdf=nanopub_rdf, source_uri=uri)

    def publish(self, nanopub: Nanopub):
        """
        Publish nanopub object.
        Uses np commandline tool to sign and publish.
        """
        # Create a temporary dir for files created during serializing and signing
        tempdir = tempfile.mkdtemp()

        # Convert nanopub rdf to trig
        fname = 'temp.trig'
        unsigned_fname = os.path.join(tempdir, fname)
        nanopub.rdf.serialize(destination=unsigned_fname, format='trig')

        # Sign the nanopub and publish it
        signed_file = java_wrapper.sign(unsigned_fname)
        nanopub_uri = java_wrapper.publish(signed_file)
        publication_info = {'nanopub_uri': nanopub_uri}
        print(f'Published to {nanopub_uri}')

        if nanopub.introduces_concept:
            # Construct the (actually published) URI of the concept being introduced by this nanopub.
            # This is only necessary if a blank node was passed as introduces_concept. In that case
            # the Nanopub.from_assertion method replaces the blank node with the base nanopub's URI
            # and appends a fragment, given by the 'name' of the blank node. For example, if a blank node
            # with name 'step' was passed as introduces_concept, the concept will be published with a URI
            # that looks like [published nanopub URI]#step.

            concept_uri = nanopub_uri + '#' + str(nanopub.introduces_concept)
            publication_info['concept_uri'] = concept_uri
            print(f'Published concept to {concept_uri}')

        return publication_info

    def claim(self, text, rdftriple=None):
        """
        Publishes a claim, either as a plain text statement, or as an rdf triple (or both)
        """
        assertion_rdf = rdflib.Graph()

        assertion_rdf.add((namespaces.AUTHOR.DrBob, namespaces.HYCL.claims, rdflib.Literal(text)))

        if rdftriple is not None:
            assertion_rdf.add(rdftriple)

        nanopub = Nanopub.from_assertion(assertion_rdf=assertion_rdf)
        self.publish(nanopub)
