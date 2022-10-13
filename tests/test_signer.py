from rdflib import BNode, Graph, Literal

from nanopub import Nanopub, namespaces
from nanopub.client import DUMMY_NAMESPACE
from nanopub.signer import add_signature
from tests.conftest import default_config, java_wrap, profile_test

# from tests.conftest import skip_if_nanopub_server_unavailable


class TestSigner:


    def test_nanopub_sign(self):
        expected_np_uri = "http://purl.org/np/RAPPd9CZrgAo_XzrDRfUtXvRYVud2PDRgCN-z7eGhIwpc"

        assertion = Graph()
        assertion.add((
            BNode('test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
        ))

        np = Nanopub(
            config=default_config,
            assertion=assertion
        )
        java_np = java_wrap.sign(np)

        signed_g = add_signature(np.rdf, profile_test, DUMMY_NAMESPACE)
        np.update_from_signed(signed_g)

        # print(np.rdf.serialize(format="trig"))
        assert np.source_uri == expected_np_uri
        assert np.source_uri == java_np



    # def test_assertion_rdf_not_mutated(self):
    #     """
    #     Check that the assertion rdf graph provided by the user
    #     is not mutated by publishing in instances where it contains
    #     a BNode.
    #     """
    #     rdf = rdflib.Graph()
    #     rdf.add((rdflib.BNode('dontchangeme'), rdflib.RDF.type, rdflib.FOAF.Person))
    #     publication = Publication.from_assertion(assertion_rdf=rdf)

    #     client = NanopubClient()
    #     client.java_wrapper.publish = mock.MagicMock()
    #     client.publish(publication)

    #     assert (rdflib.BNode('dontchangeme'), rdflib.RDF.type, rdflib.FOAF.Person) in rdf

    # def test_retract_with_force(self):
    #     client = NanopubClient()
    #     client.java_wrapper.publish = mock.MagicMock()
    #     client.retract('http://www.example.com/my-nanopub', force=True)

    # TODO: Not sure how to use mocks in this case (we want to get rid of the static get_public_key)
    # @mock.patch('nanopub.client.profile.get_public_key')
    # def test_retract_without_force(self, mock_get_public_key):
    #     test_uri = 'http://www.example.com/my-nanopub'
    #     test_public_key = 'test key'
    #     client = NanopubClient()
    #     client.java_wrapper.publish = mock.MagicMock()

    #     # Return a mocked to-be-retracted publication object that is signed with public key
    #     mock_publication = mock.MagicMock()
    #     mock_publication.pubinfo = rdflib.Graph()
    #     mock_publication.signed_with_public_key = test_public_key
    #     client.fetch = mock.MagicMock(return_value=mock_publication)

    #     client = NanopubClient()
    #     # Retract should be successful when public keys match
    #     mock_get_public_key.return_value = test_public_key
    #     client.retract(test_uri)

    #     # And fail if they don't match
    #     mock_get_public_key.return_value = 'Different public key'
    #     with pytest.raises(AssertionError):
    #         client.retract(test_uri)
