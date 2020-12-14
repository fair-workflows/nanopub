# -*- coding: utf-8 -*-
"""This module includes a client for the nanopub server.
"""

import os
import random
import tempfile
import warnings
from typing import List, Union

import rdflib
import requests

from nanopub import namespaces, profile
from nanopub.definitions import DUMMY_NANOPUB_URI
from nanopub.java_wrapper import JavaWrapper
from nanopub.publication import Publication

NANOPUB_GRLC_URLS = ["http://grlc.nanopubs.lod.labs.vu.nl/api/local/local/",
                     "http://130.60.24.146:7881/api/local/local/",
                     "https://openphacts.cs.man.ac.uk/nanopub/grlc/api/local/local/",
                     "https://grlc.nanopubs.knows.idlab.ugent.be/api/local/local/",
                     "http://grlc.np.scify.org/api/local/local/",
                     "http://grlc.np.dumontierlab.com/api/local/local/"]
NANOPUB_TEST_GRLC_URL = 'http://test-grlc.nanopubs.lod.labs.vu.nl/api/local/local/'
NANOPUB_FETCH_FORMAT = 'trig'
NANOPUB_TEST_URL = 'http://test-server.nanopubs.lod.labs.vu.nl/'


class NanopubClient:
    """
    Provides utility functions for searching, creating and publishing RDF graphs
    as assertions in a nanopublication.

    Args:
        use_test_server (bool): Toggle using the test nanopub server.

    """
    def __init__(self, use_test_server=False):
        self.use_test_server = use_test_server
        self.java_wrapper = JavaWrapper(use_test_server=use_test_server)
        if use_test_server:
            self.grlc_urls = [NANOPUB_TEST_GRLC_URL]
        else:
            self.grlc_urls = NANOPUB_GRLC_URLS

    def find_nanopubs_with_text(self, text: str, pubkey: str = None,
                                filter_retracted: bool = True, max_num_results: int = 1000):
        """Text search.

        Search the nanopub servers for any nanopubs matching the
        given search text.

        Args:
            text (str): The text to search on
            pubkey (str): Public key that the matching nanopubs should be signed with
            filter_retracted (bool): Toggle filtering for publications that are
                retracted. Default is True, returning only publications that are not retracted.
            max_num_results (int): Maximum number of result, default = 1000

        Returns:
            List of dicts depicting matching nanopublications.
            Each dict holds: 'np': the nanopublication uri,
            'date': date of creation of the nanopublication,
            'description': A description of the nanopublication (if found in RDF).

        """
        if len(text) == 0:
            return []
        endpoint = 'find_signed_nanopubs_with_text'
        params = {'text': text, 'graphpred': '', 'month': '', 'day': '', 'year': ''}
        if pubkey:
            params['pubkey'] = pubkey
        if filter_retracted:
            endpoint = 'find_valid_signed_nanopubs_with_text'
        return self._search(endpoint=endpoint,
                            params=params,
                            max_num_results=max_num_results)

    def find_nanopubs_with_pattern(self, subj: str = None, pred: str = None, obj: str = None,
                                   filter_retracted: bool = True, pubkey: str = None,
                                   max_num_results: int = 1000):
        """Pattern search.

        Search the nanopub servers for any nanopubs matching the given RDF pattern. You can leave
        parts of the triple to match anything by not specifying subj, pred, or obj arguments.

        Args:
            subj (str): URI of the subject that you want to match triples on.
            pred (str): URI of the predicate that you want to match triples on.
            obj (str): URI of the object that you want to match triples on.
            pubkey (str): Public key that the matching nanopubs should be signed with
            filter_retracted (bool): Toggle filtering for publications that are
                retracted. Default is True, returning only publications that are not retracted.
            max_num_results (int): Maximum number of result, default = 1000

        Returns:
            List of dicts depicting matching nanopublications.
            Each dict holds: 'np': the nanopublication uri,
            'date': date of creation of the nanopublication,
            'description': A description of the nanopublication (if found in RDF).

        """
        params = {}
        endpoint = 'find_signed_nanopubs_with_pattern'
        if subj:
            params['subj'] = subj
        if pred:
            params['pred'] = pred
        if obj:
            params['obj'] = obj
        if pubkey:
            params['pubkey'] = pubkey
        if filter_retracted:
            endpoint = 'find_valid_signed_nanopubs_with_pattern'

        return self._search(endpoint=endpoint,
                            params=params,
                            max_num_results=max_num_results)

    def find_things(self, type: str, searchterm: str = ' ', pubkey: str = None,
                    filter_retracted: bool = True, max_num_results=1000):
        """Search things (experimental).

        Search for any nanopublications that introduce a concept of the given type, that contain
        text with the given search term.

        Args:
            type (str): A URI denoting the type of the introduced concept
            searchterm (str): The term that you want to search on
            pubkey (str): Public key that the matching nanopubs should be signed with
            filter_retracted (bool): Toggle filtering for publications that are
                retracted. Default is True, returning only publications that are not retracted.
            max_num_results (int): Maximum number of result, default = 1000

        Returns:
            List of dicts depicting matching nanopublications.
            Each dict holds: 'np': the nanopublication uri,
            'date': date of creation of the nanopublication,
            'description': A description of the nanopublication (if found in RDF).

        """
        if searchterm == '':
            raise ValueError(f'Searchterm can not be an empty string: {searchterm}')
        endpoint = 'find_signed_things'
        params = dict()
        params['type'] = type
        params['searchterm'] = searchterm
        if pubkey:
            params['pubkey'] = pubkey
        if filter_retracted:
            endpoint = 'find_valid_signed_things'

        return self._search(endpoint=endpoint,
                            params=params,
                            max_num_results=max_num_results)

    def find_retractions_of(self, source: Union[str, Publication], valid_only=True) -> List[str]:
        """Find retractions of given URI

        Find all nanopublications that retract a certain nanopublication.

        Args:
            source (str or nanopub.Publication): URI or Publication object to find retractions for
            valid_only (bool): Toggle returning only valid retractions, i.e. retractions that are
                signed with the same public key as the publication they retract. Default is True.

        Returns:
            List of uris that retract the given URI
        """

        if isinstance(source, Publication):
            if source.is_test_publication and not self.use_test_server:
                warnings.warn('You are trying to find retractions on the production server, '
                              'whereas this publication lives on the test server')
            elif not source.is_test_publication and self.use_test_server:
                warnings.warn('You are trying to find retractions on the test server, '
                              'whereas this publication lives on the production server')
            uri = source.source_uri
        else:
            uri = source

        if valid_only:
            source_publication = self.fetch(uri)
            public_key = source_publication.signed_with_public_key
            if public_key is None:
                raise ValueError('The source publication is not signed with a public key')
        else:
            public_key = None

        results = self.find_nanopubs_with_pattern(pred=namespaces.NPX.retracts,
                                                  obj=rdflib.URIRef(uri),
                                                  pubkey=public_key,
                                                  filter_retracted=False)
        return [result['np'] for result in results]

    def _query_grlc(self, params, endpoint):
        """Query the nanopub server grlc endpoint.

        Query a nanopub grlc server endpoint (for example: find_text). Try several of the nanopub
        garlic servers.
        """
        headers = {"Accept": "application/json"}
        r = None
        random.shuffle(self.grlc_urls)  # To balance load across servers
        for grlc_url in self.grlc_urls:
            url = grlc_url + endpoint
            r = requests.get(url, params=params, headers=headers)
            if r.status_code == 502:  # Server is likely down
                warnings.warn(f'Could not get response from {grlc_url}, trying other servers')
            else:
                r.raise_for_status()  # For non-502 errors we don't want to try other servers
                return r

        raise requests.HTTPError(f'Could not get response from any of the nanopub grlc '
                                 f'endpoints, last response: {r.status_code}:{r.reason}')

    def _search(self, endpoint: str, params: dict, max_num_results: int):
        """
        General nanopub server search method. User should use e.g. find_nanopubs_with_text,
        find_things etc.

        Args:
            endpoint: garlic endpoint to query, for example: find_things
            params: dictionary with parameters for get request
            max_num_results: Maximum number of results to return

        Raises:
            JSONDecodeError: in case response can't be serialized as JSON, this can happen due to a
                virtuoso error.
        """
        r = self._query_grlc(params, endpoint)
        results_json = r.json()

        results_list = results_json['results']['bindings']
        nanopubs = []

        for result in results_list:
            nanopubs.append(self._parse_search_result(result))
            if len(nanopubs) >= max_num_results:
                break

        return nanopubs

    @staticmethod
    def _parse_search_result(result: dict):
        """
        Parse a nanopub search result (i.e. referring to one matching nanopublication).
        Rename 'v' to 'description', select only date, np and description fields and unnest them.
        """
        parsed = dict()
        parsed['np'] = result['np']['value']

        if 'v' in result:
            parsed['description'] = result['v']['value']
        elif 'description' in result:
            parsed['description'] = result['description']['value']
        else:
            parsed['description'] = ''
        parsed['date'] = result['date']['value']
        return parsed

    def fetch(self, uri: str):
        """Fetch nanopublication

        Download the nanopublication at the specified URI.

        Args:
            uri (str): The URI of the nanopublication to fetch.

        Returns:
            Publication: a Publication object representing the nanopublication.
        """
        r = requests.get(uri + '.' + NANOPUB_FETCH_FORMAT)
        if not r.ok and self.use_test_server:
            # Let's try the test server
            nanopub_id = uri.rsplit('/', 1)[-1]
            uri = NANOPUB_TEST_URL + nanopub_id
            r = requests.get(uri + '.' + NANOPUB_FETCH_FORMAT)
        r.raise_for_status()

        nanopub_rdf = rdflib.ConjunctiveGraph()
        nanopub_rdf.parse(data=r.text, format=NANOPUB_FETCH_FORMAT)
        return Publication(rdf=nanopub_rdf, source_uri=uri)

    def publish(self, publication: Publication):
        """Publish a Publication object.

        Publish Publication object to the nanopub server. It uses nanopub_java commandline tool to
        sign the nanopublication RDF with the RSA key in the profile and then publish.

        Args:
            publication (Publication): Publication object to publish.

        Returns:
            dict of str: Publication info with: 'nanopub_uri': the URI of the published
            nanopublication, 'concept_uri': the URI of the introduced concept (if applicable)

        """
        # Create a temporary dir for files created during serializing and signing
        tempdir = tempfile.mkdtemp()

        # Convert nanopub rdf to trig
        fname = 'temp.trig'
        unsigned_fname = os.path.join(tempdir, fname)
        publication.rdf.serialize(destination=unsigned_fname, format='trig')

        # Sign the nanopub and publish it
        signed_file = self.java_wrapper.sign(unsigned_fname)
        nanopub_uri = self.java_wrapper.publish(signed_file)
        publication_info = {'nanopub_uri': nanopub_uri}
        print(f'Published to {nanopub_uri}')

        if publication.introduces_concept:
            concept_uri = str(publication.introduces_concept)
            # Replace the DUMMY_NANOPUB_URI with the actually published nanopub uri. This is
            # necessary if a blank node was passed as introduces_concept. In that case the
            # Nanopub.from_assertion method replaces the blank node with the base nanopub's URI
            # and appends a fragment, given by the 'name' of the blank node. For example, if a
            # blank node with name 'step' was passed as introduces_concept, the concept will be
            # published with a URI that looks like [published nanopub URI]#step.
            concept_uri = concept_uri.replace(DUMMY_NANOPUB_URI, nanopub_uri)
            publication_info['concept_uri'] = concept_uri
            print(f'Published concept to {concept_uri}')

        return publication_info

    def claim(self, statement_text: str):
        """Quickly claim a statement.

        Constructs statement triples around the provided text following the Hypotheses and Claims
        Ontology (http://purl.org/petapico/o/hycl).

        Args:
            statement_text (str): the text of the statement, example: 'All cats are grey'

        Returns:
            dict of str: Publication info with: 'nanopub_uri': the URI of the published
            nanopublication, 'concept_uri': the URI of the introduced concept (if applicable)

        """
        assertion_rdf = rdflib.Graph()
        this_statement = rdflib.term.BNode('mystatement')
        assertion_rdf.add((this_statement, rdflib.RDF.type, namespaces.HYCL.Statement))
        assertion_rdf.add((this_statement, rdflib.RDFS.label, rdflib.Literal(statement_text)))

        provenance_rdf = rdflib.Graph()
        orcid_id_uri = rdflib.URIRef(profile.get_orcid_id())
        provenance_rdf.add((orcid_id_uri, namespaces.HYCL.claims, this_statement))
        publication = Publication.from_assertion(assertion_rdf=assertion_rdf,
                                                 attribute_assertion_to_profile=True,
                                                 provenance_rdf=provenance_rdf)
        return self.publish(publication)

    def _check_public_keys_match(self, uri):
        """ Check for matching public keys of a nanopublication with the profile.

        Raises:
            AssertionError: When the nanopublication is signed with a public key that does not
                match the public key in the profile
        """
        publication = self.fetch(uri)
        their_public_key = publication.signed_with_public_key
        if their_public_key is not None and their_public_key != profile.get_public_key():
            raise AssertionError('The public key in your profile does not match the public key'
                                 'that the publication that you want to retract is signed '
                                 'with. Use force=True to force retraction anyway.')

    def retract(self, uri: str, force=False):
        """Retract a nanopublication.

        Publish a retraction nanpublication that declares retraction of the nanopublication that
        corresponds to the 'uri' argument.

        Args:
            uri (str): The uri pointing to the to-be-retracted nanopublication
            force (bool): Toggle using force to retract, this will even retract the
                nanopublication if it is signed with a different public key than the one
                in the user profile.

        Returns:
            dict of str: Publication info with: 'nanopub_uri': the URI of the published
            nanopublication, 'concept_uri': the URI of the introduced concept (if applicable)
        """
        if not force:
            self._check_public_keys_match(uri)
        assertion_rdf = rdflib.Graph()
        orcid_id = profile.get_orcid_id()
        assertion_rdf.add((rdflib.URIRef(orcid_id), namespaces.NPX.retracts,
                           rdflib.URIRef(uri)))
        publication = Publication.from_assertion(assertion_rdf=assertion_rdf,
                                                 attribute_assertion_to_profile=True)
        return self.publish(publication)
