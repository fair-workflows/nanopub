from rdflib import RDF, BNode, ConjunctiveGraph, Graph, Literal, URIRef

from nanopub import Nanopub, NanopubConfig, namespaces
from tests.conftest import default_config, java_wrap, profile_test

config_testsuite = NanopubConfig(
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=False,
    attribute_publication_to_profile=False,
    profile=profile_test,
    use_test_server=True,
)

class TestNanopublication:

    def test_nanopub_sign_uri(self):
        expected_np_uri = "http://purl.org/np/RAoXkQkJe_lpMhYW61Y9mqWDHa5MAj1o4pWIiYLmAzY50"
        assertion = Graph()
        assertion.add((
            URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
        ))

        np = Nanopub(
            config=default_config,
            assertion=assertion
        )
        java_np = java_wrap.sign(np)
        np.sign()
        print(np.source_uri)

        assert np.source_uri == expected_np_uri
        assert np.source_uri == java_np


    def test_nanopub_sign_bnode(self):
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
        np.sign()
        print(np.source_uri)
        # print(np.rdf.serialize(format='trig'))
        assert np.source_uri == expected_np_uri
        assert np.source_uri == java_np


    def test_nanopub_publish(self):
        expected_np_uri = "http://purl.org/np/RAoXkQkJe_lpMhYW61Y9mqWDHa5MAj1o4pWIiYLmAzY50"
        assertion = Graph()
        assertion.add((
            URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
        ))
        np = Nanopub(
            config=default_config,
            assertion=assertion
        )
        java_np = java_wrap.sign(np)
        np.publish()
        assert np.source_uri == expected_np_uri
        assert np.source_uri == java_np


    def test_nanopub_signed_testsuite1(self):
        expected_np_uri = "http://example.org/nanopub-validator-example/RALbDbWVnLmLqpNgOsI_AaYfLbEnlOfZy3CoRRLs9XqVk"
        # java -jar lib/nanopub-1.38-jar-with-dependencies.jar sign tests/testsuite/transform/signed/rsa-key1/simple1.in.trig

        np_g = ConjunctiveGraph()
        np_g.parse("./tests/testsuite/transform/signed/rsa-key1/simple1.in.trig", format="trig")

        out_g = ConjunctiveGraph()
        out_g.parse("./tests/testsuite/transform/signed/rsa-key1/simple1.out.trig", format="trig")
        out_source_uri = str(list(
            out_g.subjects(
                predicate=RDF.type, object=namespaces.NP.Nanopublication
            )
        )[0])


        np = Nanopub(
            config=config_testsuite,
            rdf=np_g
        )
        java_np = java_wrap.sign(np)
        np.sign()
        print(np)
        # print(np.source_uri)
        # # print(np.rdf.serialize(format='trig'))
        assert np.source_uri == expected_np_uri
        # print(java_np)
        assert np.source_uri == java_np
        assert np.source_uri == out_source_uri


    def test_nanopub_testsuite(self):
        test_files = [
            "./tests/testsuite/transform/signed/rsa-key1/simple1.in.trig",
            "./tests/testsuite/transform/trusty/aida1.in.trig",
            "./tests/testsuite/transform/trusty/simple1.in.trig",
            "./tests/testsuite/valid/plain/aida1.trig",
            "./tests/testsuite/valid/plain/simple1.nq",
            "./tests/testsuite/valid/plain/simple1.trig",
            "./tests/testsuite/valid/plain/simple1.xml",

        ]
        # java -jar lib/nanopub-1.38-jar-with-dependencies.jar sign tests/testsuite/transform/signed/rsa-key1/simple1.in.trig

        for test_file in test_files:
            np_g = ConjunctiveGraph()
            if test_file.endswith(".xml"):
                np_g.parse(test_file, format="trix")
            else:
                np_g.parse(test_file)

            np = Nanopub(
                config=config_testsuite,
                rdf=np_g
            )
            java_np = java_wrap.sign(np)
            np.sign()
            assert np.source_uri == java_np



    # def test_nanopub_claim(self):
    #     client = NanopubClient(profile=profile_test, use_test_server=True)
    #     np = client.claim(statement_text='Some controversial statement')
    #     assert np.source_uri is not None

    # def test_nanopub_retract(self):
    #     client = NanopubClient(profile=profile_test, use_test_server=True)
    #     np = client.retract(uri='http://purl.org/np/RAnksi2yDP7jpe7F6BwWCpMOmzBEcUImkAKUeKEY_2Yus', force=True)
    #     assert np.source_uri is not None



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
