from unittest import mock

import pytest
import rdflib

from conftest import skip_if_nanopub_server_unavailable
from nanopub import NanopubClient, namespaces, Publication

client = NanopubClient(use_test_server=True)

TEST_ASSERTION = (namespaces.AUTHOR.DrBob, namespaces.HYCL.claims, rdflib.Literal('This is a test'))


class TestNanopubClient:

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_nanopubs_with_text(self):
        """
        Check that Nanopub text search is returning results for a few common search terms
        """
        searches = ['test', 'US']

        for search in searches:
            results = client.find_nanopubs_with_text(search)
            assert len(results) > 0

        assert len(client.find_nanopubs_with_text('')) == 0

    @pytest.mark.flaky(max_runs=10)
    def test_find_nanopubs_with_text_prod(self):
        """
        Check that Nanopub text search is returning results for a few common search terms on the
        production nanopub server
        """
        prod_client = NanopubClient()
        searches = ['test', 'US']
        for search in searches:
            results = prod_client.find_nanopubs_with_text(search)
            assert len(results) > 0

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_nanopubs_with_pattern(self):
        """
            Check that Nanopub pattern search is returning results
        """
        searches = [
            ('', 'http://example.org/transmits', 'http://example.org/malaria'),
            ('http://purl.org/np/RA8ui7ddvV25m1qdyxR4lC8q8-G0yb3SN8AC0Bu5q8Yeg', '', '')
        ]

        for subj, pred, obj in searches:
            results = client.find_nanopubs_with_pattern(subj=subj, pred=pred, obj=obj)
            assert len(results) > 0
            assert 'Error' not in results[0]

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_nanopub_find_things(self):
        """
        Check that Nanopub 'find_things' search is returning results
        """
        results = client.find_things(type='http://purl.org/net/p-plan#Plan')
        assert len(results) > 0

        with pytest.raises(Exception):
            client.find_things()

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_valid_signed_nanopubs_with_text(self):
        """
        Check that Nanopub text search is returning results for a few common search terms
        for signed and not retracted nanopubs
        """
        searches = ['covid-19', 'europe']

        for search in searches:
            results = client.find_valid_signed_nanopubs_with_text(search)
            assert len(results) > 0

        assert len(client.find_valid_signed_nanopubs_with_text('')) == 0

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_valid_signed_nanopubs_with_pattern(self):
        """
            Check that Nanopub pattern search is returning results
            for signed and not retracted nanopubs
        """
        searches = [
          ('', '', ''),
          ('', '', 'http://purl.org/net/p-plan#Plan'),
          ('', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'http://purl.org/net/p-plan#Plan')
        ]

        for subj, pred, obj in searches:
            results = client.find_valid_signed_nanopubs_with_pattern(subj=subj, pred=pred, obj=obj)
            assert len(results) > 0
            assert 'Error' not in results[0]

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_nanopub_find_valid_signed_things(self):
        """
        Check that Nanopub 'find_things' search is returning results
        for signed and not retracted nanopubs
        """
        results = client.find_valid_signed_things(type='http://purl.org/net/p-plan#Plan')
        assert len(results) > 0

        with pytest.raises(Exception):
            client.find_valid_signed_things()

    def test_nanopub_search(self):
        with pytest.raises(Exception):
            client._search(params=None,
                           max_num_results=100,
                           endpoint='http://www.api.url')
        with pytest.raises(Exception):
            client._search(params={'search': 'text'},
                           max_num_results=None,
                           endpoint='http://www.api.url')
        with pytest.raises(Exception):
            client._search(params={'search': 'text'},
                           max_num_results=100,
                           endpoint=None)

    @pytest.mark.parametrize(
        "test_input,expected",
        [   # Input with 'v'
            ({'np': {'value': 'test_nanopub_uri'},
              'v': {'value': 'test_description'},
              'date': {'value': '01-01-2001'}},
             {'np': 'test_nanopub_uri',
              'description': 'test_description',
              'date': '01-01-2001'}),
            # Input with 'description'
            ({'np': {'value': 'test_nanopub_uri'},
              'description': {'value': 'test_description'},
              'date': {'value': '01-01-2001'}},
             {'np': 'test_nanopub_uri',
              'description': 'test_description',
              'date': '01-01-2001'}),
            # Input without 'v' or 'description'
            ({'np': {'value': 'test_nanopub_uri'},
              'date': {'value': '01-01-2001'}},
             {'np': 'test_nanopub_uri',
              'description': '',
              'date': '01-01-2001'}),
            # Input without 'v' or 'description' and irrelevant fields
            ({'np': {'value': 'test_nanopub_uri'},
              'date': {'value': '01-01-2001'},
              'irrelevant': {'value': 'irrelevant_value'}},
             {'np': 'test_nanopub_uri',
              'description': '',
              'date': '01-01-2001'})
         ])
    def test_parse_search_result(self, test_input, expected):
        assert client._parse_search_result(test_input) == expected

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_nanopub_fetch(self):
        """
        Check that Nanopub fetch is returning results for a few known nanopub URIs.
        """
        known_nps = [
            'http://purl.org/np/RANGY8fx_EYVeZzJOinH9FoY-WrQBerKKUy2J9RCDWH6U',
            'http://purl.org/np/RAABh3eQwmkdflVp50zYavHUK0NgZE2g2ewS2j4Ur6FHI',
            'http://purl.org/np/RA8to60YFWSVCh2n_iyHZ2yiYEt-hX_DdqbWa5yI9r-gI'
        ]

        for np_uri in known_nps:
            np = client.fetch(np_uri)
            assert isinstance(np, Publication)
            assert len(np.rdf) > 0
            assert np.assertion is not None
            assert np.pubinfo is not None
            assert np.provenance is not None
            assert len(np.__str__()) > 0

    def test_nanopub_claim(self):
        client = NanopubClient()
        client.java_wrapper.publish = mock.MagicMock()
        client.claim(statement_text='Some controversial statement')

    def test_nanopub_publish(self):
        test_concept = rdflib.term.BNode('test')
        test_published_uri = 'http://www.example.com/my-nanopub'
        expected_concept_uri = 'http://www.example.com/my-nanopub#test'
        client = NanopubClient()
        client.java_wrapper.publish = mock.MagicMock(return_value=test_published_uri)
        assertion_rdf = rdflib.Graph()
        assertion_rdf.add(
            (test_concept, namespaces.HYCL.claims, rdflib.Literal('This is a test')))

        nanopub = Publication.from_assertion(
            assertion_rdf=assertion_rdf,
            introduces_concept=test_concept,
        )
        pubinfo = client.publish(nanopub)
        assert pubinfo['nanopub_uri'] == test_published_uri
        assert pubinfo['concept_uri'] == expected_concept_uri

    def test_retract_with_force(self):
        client = NanopubClient()
        client.java_wrapper.publish = mock.MagicMock()
        client.retract('http://www.example.com/my-nanopub', force=True)

    @mock.patch('nanopub.client.profile.get_public_key')
    def test_retract_without_force(self, mock_get_public_key):
        test_uri = 'http://www.example.com/my-nanopub'
        test_public_key = 'test key'
        client = NanopubClient()
        client.java_wrapper.publish = mock.MagicMock()

        # Return a mocked to-be-retracted publication object that is signed with public key
        mock_publication = mock.MagicMock()
        mock_publication.pubinfo = rdflib.Graph()
        mock_publication.pubinfo.add((rdflib.URIRef(test_uri + '#sig'),
                                      namespaces.NPX.hasPublicKey,
                                      rdflib.Literal(test_public_key)))
        client.fetch = mock.MagicMock(return_value=mock_publication)

        # Retract should be successful when public keys match
        mock_get_public_key.return_value = test_public_key
        client.retract(test_uri)

        # And fail if they don't match
        mock_get_public_key.return_value = 'Different public key'
        with pytest.raises(AssertionError):
            client.retract(test_uri)
