import os
import tempfile

from rdflib import BNode, Graph, Literal, URIRef

from nanopub import NanopubClient, NanopubConfig, namespaces, load_profile, Nanopublication
from nanopub.definitions import TEST_RESOURCES_FILEPATH
from tests.conftest import test_profile_path
from tests.java_wrapper import JavaWrapper
# from tests.conftest import skip_if_nanopub_server_unavailable

profile = load_profile(test_profile_path)
config = NanopubConfig(
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=True,
    attribute_publication_to_profile=True,
    assertion_attributed_to=None,
    publication_attributed_to=None,
    derived_from=None
)
client = NanopubClient(
    use_test_server=True,
    profile=profile,
    nanopub_config=config
)

java_wrap = JavaWrapper(private_key=profile.private_key)


class TestNanopublication:

    def test_nanopub_sign_uri(self):
        expected_np_uri = "http://purl.org/np/RANn9T0QMUldZhm6dlUHtOCvwALxE3UTJeVZ0M9qGT-qk"
        assertion = Graph()
        assertion.add((
            URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
        ))

        # np = client.create_nanopub(
        #     assertion=assertion,
        #     # introduces_concept=test_concept,
        # )
        np = Nanopublication(
            config=config,
            profile=profile,
            assertion=assertion
        )
        java_np = java_wrap.sign(np)

        np = client.sign(np)

        # print(np.rdf.serialize(format="trig"))
        # print(np.source_uri)
        # print(expected_np_uri)
        assert np.source_uri == expected_np_uri
        assert np.source_uri == java_np


    def test_nanopub_sign_bnode(self):
        expected_np_uri = "http://purl.org/np/RAmdN3ynXoyMki1Ab9j9O4KWnX2hj7ETw3PdKtOMkpvhY"

        assertion = Graph()
        assertion.add((
            BNode('test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
        ))

        np = Nanopublication(
            config=config,
            profile=profile,
            assertion=assertion
        )
        np = client.sign(np)
        # print(np.rdf.serialize(format='trig'))
        assert np.source_uri == expected_np_uri



    def test_nanopub_publish(self):
        expected_np_uri = "http://purl.org/np/RANn9T0QMUldZhm6dlUHtOCvwALxE3UTJeVZ0M9qGT-qk"
        assertion = Graph()
        assertion.add((
            URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
        ))
        np = Nanopublication(
            config=config,
            profile=profile,
            assertion=assertion
        )
        np = client.publish(np)
        assert np.source_uri == expected_np_uri



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
