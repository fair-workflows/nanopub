import pytest
from rdflib import BNode, Graph, Literal, URIRef

from nanopub import Nanopub, NanopubClaim, NanopubConf, NanopubRetract, create_nanopub_index, namespaces
from nanopub.templates.nanopub_introduction import NanopubIntroduction
from tests.conftest import default_config, java_wrap, profile_test, skip_if_nanopub_server_unavailable

config_testsuite = NanopubConf(
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=False,
    attribute_publication_to_profile=False,
    profile=profile_test,
    use_test_server=True,
)


def test_nanopub_sign_uri():
    expected_np_uri = "http://purl.org/np/RAoXkQkJe_lpMhYW61Y9mqWDHa5MAj1o4pWIiYLmAzY50"
    assertion = Graph()
    assertion.add((
        URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
    ))

    np = Nanopub(
        conf=default_config,
        assertion=assertion
    )
    java_np = java_wrap.sign(np)
    np.sign()
    assert np.has_valid_signature
    assert np.source_uri == expected_np_uri
    assert np.source_uri == java_np



def test_nanopub_sign_uri2():
    expected_np_uri = "http://purl.org/np/RAoXkQkJe_lpMhYW61Y9mqWDHa5MAj1o4pWIiYLmAzY50"
    np = Nanopub(
        conf=default_config,
    )
    np.assertion.add((
        URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
    ))
    java_np = java_wrap.sign(np)
    np.sign()
    assert np.has_valid_signature
    assert np.source_uri == expected_np_uri
    assert np.source_uri == java_np


def test_nanopub_sign_bnode():
    expected_np_uri = "http://purl.org/np/RAclARDMZxQ0yLKu3enKS4-CGubi2coQUvyb7BXF3XRvY"
    assertion = Graph()
    assertion.add((
        BNode('test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
    ))

    np = Nanopub(
        conf=default_config,
        assertion=assertion
    )
    np.sign()
    print(np.source_uri)
    assert np.has_valid_signature
    assert np.source_uri == expected_np_uri


def test_nanopub_sign_bnode2():
    expected_np_uri = "http://purl.org/np/RA2bruKoZi0snNNfQCkB2qvhCnscTt9Wmz2_rSGnwB2nQ"
    assertion = Graph()
    assertion.add((
        BNode('test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
    ))
    assertion.add((
        BNode('test2'), namespaces.HYCL.claims, Literal('This is another test of nanopub-python')
    ))

    np = Nanopub(
        conf=default_config,
        assertion=assertion
    )
    np.sign()
    print(np)
    assert np.source_uri == expected_np_uri


def test_nanopub_publish():
    expected_np_uri = "http://purl.org/np/RAoXkQkJe_lpMhYW61Y9mqWDHa5MAj1o4pWIiYLmAzY50"
    assertion = Graph()
    assertion.add((
        URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
    ))
    np = Nanopub(
        conf=default_config,
        assertion=assertion
    )
    java_np = java_wrap.sign(np)
    np.publish()
    assert np.has_valid_signature
    assert np.source_uri == expected_np_uri
    assert np.source_uri == java_np



def test_nanopub_claim():
    np = NanopubClaim(
        claim='Some controversial statement',
        conf=config_testsuite,
    )
    java_np = java_wrap.sign(np)
    np.sign()
    assert np.source_uri is not None
    assert np.source_uri == java_np


def test_nanopub_retract():
    np = NanopubRetract(
        uri='http://purl.org/np/RAnksi2yDP7jpe7F6BwWCpMOmzBEcUImkAKUeKEY_2Yus',
        force=True,
        conf=config_testsuite,
    )
    java_np = java_wrap.sign(np)
    np.sign()
    assert np.source_uri is not None
    assert np.source_uri == java_np


def test_nanopub_introduction():
    np = NanopubIntroduction(
        conf=config_testsuite,
        host="http://test"
    )
    java_np = java_wrap.sign(np)
    np.sign()
    assert np.source_uri is not None
    assert np.source_uri == java_np


def test_nanopub_index():
    np_list = create_nanopub_index(
        conf=config_testsuite,
        np_list=[
            "https://purl.org/np/RAD28Nl4h_mFH92bsHUrtqoU4C6DCYy_BRTvpimjVFgJo",
            "https://purl.org/np/RAEhbEJ1tdhPqM6gNPScX9vIY1ZtUzOz7woeJNzB3sh3E",
        ],
        title="My nanopub index",
        description="This is my nanopub index",
        creation_time="2020-09-21T00:00:00",
        creators=["https://orcid.org/0000-0000-0000-0000"],
        see_also="https://github.com/fair-workflows/nanopub",
    )
    for np in np_list:
        assert np.source_uri is not None


@pytest.mark.flaky(max_runs=10)
@skip_if_nanopub_server_unavailable
def test_nanopub_fetch():
    """Check that creating Nanopub from source URI (fetch) works for a few known nanopub URIs."""
    known_nps = [
        'http://purl.org/np/RANGY8fx_EYVeZzJOinH9FoY-WrQBerKKUy2J9RCDWH6U',
        'http://purl.org/np/RAABh3eQwmkdflVp50zYavHUK0NgZE2g2ewS2j4Ur6FHI',
        'http://purl.org/np/RA8to60YFWSVCh2n_iyHZ2yiYEt-hX_DdqbWa5yI9r-gI'
    ]
    for np_uri in known_nps:
        np = Nanopub(
            source_uri=np_uri,
            conf=NanopubConf(use_test_server=True)
        )
        print(np)
        assert len(np.rdf) > 0
        assert np.assertion is not None
        assert np.pubinfo is not None
        assert np.provenance is not None
        assert np.is_valid


def test_unvalid_fetch():
    try:
        publication = Nanopub(source_uri='http://a-real-server/example')
        assert publication.is_valid
    except Exception:
        assert True
