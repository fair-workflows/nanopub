from rdflib import BNode, Graph, Literal

from nanopub import Nanopub, namespaces
from nanopub.client import DUMMY_NAMESPACE
from nanopub.signer import add_signature
from tests.conftest import default_config, java_wrap, profile_test


def test_nanopub_sign():
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
    assert np.source_uri == expected_np_uri
    assert np.source_uri == java_np
