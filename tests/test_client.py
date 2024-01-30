import pytest
from rdflib import RDF, URIRef

from nanopub import NanopubClient
from nanopub.definitions import TEST_RESOURCES_FILEPATH
from tests.conftest import skip_if_nanopub_server_unavailable

client = NanopubClient(use_test_server=True)
prod_client = NanopubClient(use_test_server=False)

PUBKEY = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCuZe/66Yn1/kZ+TrhkAUez7n3x/dbukNAxprC2I4n/' \
    'by5dAgSHvnRm7zhEeDyFFHXNm2PBqj3uLOEM6m2lWDsCmTHojgLUBpvhCzvziSjAzBJ4loLaax+Nt1hSY2/' \
    'MNB0xJKtxQz7xe8gPf6iyckD/H7Mwa9mx5ncYRzg5XUlvvQIDAQAB'

NANOPUB_SAMPLE_SIGNED = str(TEST_RESOURCES_FILEPATH / 'nanopub_sample_signed.trig')


class TestNanopubClient:

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_nanopubs_with_text(self):
        """
        Check that Nanopub text search is returning results for a few common search terms
        """
        searches = ['citation', 'comment']

        for search in searches:
            results = list(client.find_nanopubs_with_text(search))
            assert len(results) > 0
        results = list(client.find_nanopubs_with_text(''))
        assert len(results) == 0

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_nanopubs_with_text_pubkey(self):
        results = list(client.find_nanopubs_with_text('comment', pubkey=PUBKEY))
        assert len(results) > 0

        results = list(client.find_nanopubs_with_text('comment', pubkey='wrong'))
        assert len(results) == 0

    @pytest.mark.flaky(max_runs=10)
    def test_find_nanopubs_with_text_prod(self):
        """
        Check that Nanopub text search is returning results for a few common search terms on the
        production nanopub server
        """
        prod_client = NanopubClient()
        searches = ['citation', "chemical"]
        for search in searches:
            results = list(prod_client.find_nanopubs_with_text(search))
            assert len(results) > 0

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_nanopubs_with_text_json_not_returned(self):
        """
        Check that text search that triggers a virtuoso error is handled correctly. In such a
        case HTML is returned by the server rather than JSON.
        """
        results = client.find_nanopubs_with_text(
            'a string that is not in any of the nanopublications'
            ' and that virtuoso does not like')

        with pytest.raises(ValueError):
            list(results)

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_nanopubs_with_pattern(self):
        """
            Check that Nanopub pattern search is returning results
        """
        searches = [
            ('', RDF.type, URIRef("http://www.w3.org/ns/oa#Annotation")),
            ('https://w3id.org/np/RAj75Z7QMYNalgNiMG9IthMuj18VuJbto9sC8Jl6lp9WM#_1', '', '')
        ]

        for subj, pred, obj in searches:
            results = list(client.find_nanopubs_with_pattern(subj=subj, pred=pred, obj=obj))
            assert len(results) > 0
            assert 'Error' not in results[0]

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_nanopubs_with_pattern_pubkey(self):
        """
            Check that Nanopub pattern search is returning results
        """
        subj, pred, obj = (
            'https://w3id.org/np/RAj75Z7QMYNalgNiMG9IthMuj18VuJbto9sC8Jl6lp9WM#_1', '', '')
        results = list(client.find_nanopubs_with_pattern(subj=subj, pred=pred, obj=obj,
                                                         pubkey=PUBKEY))
        assert len(results) > 0

        results = list(client.find_nanopubs_with_pattern(subj=subj, pred=pred, obj=obj,
                                                         pubkey='wrong'))
        assert len(results) == 0

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_nanopub_find_things(self):
        """
        Check that Nanopub 'find_things' search is returning results
        """
        results = list(prod_client.find_things(type='http://purl.org/net/p-plan#Plan'))
        assert len(results) > 0

        with pytest.raises(Exception):
            list(prod_client.find_things())

        with pytest.raises(Exception):
            list(prod_client.find_things(type='http://purl.org/net/p-plan#Plan', searchterm=''))

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_find_things_pubkey(self):
        things_pubkey = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCoZmUKAHAF0CY2sKahOanR1V8wP62NOw3G0wcVLULWxqXB/gcW25bGPcA5RKoiuhT6dUbfcRXm" \
            "wLknE29h6KWfKYLtNaqdrHbjSnNC65dNmNxCNp0i6ZLZRh51mxw9IPJHZrDqQ9bcLwm9d1G1fDKasA+h1vrF3Hv1YrQsF9aW1QIDAQAB"
        results = list(prod_client.find_things(type='http://purl.org/net/p-plan#Plan', pubkey=things_pubkey))
        assert len(results) > 0

        results = list(prod_client.find_things(type='http://purl.org/net/p-plan#Plan', pubkey='wrong'))
        assert len(results) == 0

    @pytest.mark.flaky(max_runs=10)
    @skip_if_nanopub_server_unavailable
    def test_nanopub_find_things_empty_searchterm(self):
        """
        Check that Nanopub 'find_things' search raises exception if search string is empty
        """
        with pytest.raises(Exception):
            client.find_things(searchterm='')

    # TODO: find retracted in the new nanopub server to fix those tests

    # @pytest.mark.flaky(max_runs=10)
    # @skip_if_nanopub_server_unavailable
    # def test_find_things_filter_retracted(self):
    #     filtered_results = list(client.find_things(type='http://purl.org/net/p-plan#Plan',
    #                                                filter_retracted=True))
    #     assert len(filtered_results) > 0
    #     all_results = list(client.find_things(type='http://purl.org/net/p-plan#Plan',
    #                                           filter_retracted=False))
    #     assert len(all_results) > 0
    #     # The filtered results should be a smaller subset of all the results, assuming that some of
    #     # the results are retracted nanopublications.
    #     assert len(all_results) > len(filtered_results)

    # @pytest.mark.flaky(max_runs=10)
    # @skip_if_nanopub_server_unavailable
    # def test_find_retractions_of(self):
    #     uri = 'http://purl.org/np/RAnksi2yDP7jpe7F6BwWCpMOmzBEcUImkAKUeKEY_2Yus'
    #     results = client.find_retractions_of(uri, valid_only=False)
    #     expected_uris = [
    #         'http://purl.org/np/RAYhe0XddJhBsJvVt0h_aq16p6f94ymc2wS-q2BAgnPVY',
    #         'http://purl.org/np/RACdYpR-6DZnT6JkEr1ItoYYXMAILjOhDqDZsMVO8EBZI'
    #     ]
    #     for expected_uri in expected_uris:
    #         assert expected_uri in results


    # @pytest.mark.flaky(max_runs=10)
    # @skip_if_nanopub_server_unavailable
    # def test_find_retractions_of_valid_only(self):
    #     uri = 'http://purl.org/np/RAnksi2yDP7jpe7F6BwWCpMOmzBEcUImkAKUeKEY_2Yus'
    #     results = client.find_retractions_of(uri, valid_only=True)
    #     expected_uri = 'http://purl.org/np/RAYhe0XddJhBsJvVt0h_aq16p6f94ymc2wS-q2BAgnPVY'
    #     assert expected_uri in results
    #     # This is a nanopublication that is signed with a different public key than the nanopub
    #     # it retracts, so it is not valid and should not be returned.
    #     unexpected_uri = 'http://purl.org/np/RACdYpR-6DZnT6JkEr1ItoYYXMAILjOhDqDZsMVO8EBZI'
    #     assert unexpected_uri not in results

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
        ]
    )
    def test_parse_search_result(self, test_input, expected):
        assert client._parse_search_result(test_input) == expected
