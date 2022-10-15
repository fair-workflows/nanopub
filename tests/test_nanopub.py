from pathlib import Path

from rdflib import RDF, BNode, ConjunctiveGraph, Graph, Literal, URIRef

from nanopub import Nanopub, NanopubClaim, NanopubConf, NanopubRetract, create_nanopub_index, namespaces
from nanopub.definitions import MalformedNanopubError
from nanopub.templates.nanopub_introduction import NanopubIntroduction
from tests.conftest import default_config, java_wrap, profile_test

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


def test_nanopub_sign_bnode():
    expected_np_uri = "http://purl.org/np/RAPPd9CZrgAo_XzrDRfUtXvRYVud2PDRgCN-z7eGhIwpc"
    assertion = Graph()
    assertion.add((
        BNode('test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
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


def test_nanopub_sign_bnode2():
    # java -jar lib/nanopub-1.*-SNAPSHOT-jar-with-dependencies.jar sign tests/testsuite/valid/plain/bnode2.trig
    expected_np_uri = "http://purl.org/np/RAgZzcMm4bxLVPo2Ve4aOTbh_BHoyEVCxY_lMposaRar8"
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
    java_np = java_wrap.sign(np)
    np.sign()
    # TODO: When verifying with 2 BNode, they are assign unpredictably _1 and _2 to the URI
    # and creates a different URI
    # assert np.has_valid_signature
    assert np.source_uri == expected_np_uri
    assert np.source_uri == java_np


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


def test_nanopub_signed_testsuite1():
    expected_np_uri = "http://example.org/nanopub-validator-example/RALbDbWVnLmLqpNgOsI_AaYfLbEnlOfZy3CoRRLs9XqVk"
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
        conf=config_testsuite,
        rdf=np_g
    )
    java_np = java_wrap.sign(np)
    np.sign()
    assert np.has_valid_signature
    assert np.source_uri == expected_np_uri
    assert np.source_uri == java_np
    assert np.source_uri == out_source_uri


def test_nanopub_testsuite_sign_valid():
    test_files = [
        "./tests/testsuite/transform/signed/rsa-key1/simple1.in.trig",
        "./tests/testsuite/transform/trusty/aida1.in.trig",
        "./tests/testsuite/transform/trusty/simple1.in.trig",
        "./tests/testsuite/valid/plain/aida1.trig",
        "./tests/testsuite/valid/plain/simple1.nq",
        "./tests/testsuite/valid/plain/simple1.trig",
    ]

    for test_file in test_files:
        print(f'✒️ Testing signing valid nanopub: {test_file}')
        np_g = ConjunctiveGraph()
        if test_file.endswith(".xml"):
            np_g.parse(test_file, format="trix")
        else:
            np_g.parse(test_file)

        np = Nanopub(
            conf=config_testsuite,
            rdf=Path(test_file)
        )
        java_np = java_wrap.sign(np)
        np.sign()
        assert np.has_valid_signature
        assert np.is_valid
        assert np.source_uri == java_np


def test_nanopub_testsuite_sign_valid_trix():
    test_files = [
        "./tests/testsuite/valid/plain/simple1.xml",
    ]

    for test_file in test_files:
        print(f'✒️ Testing signing valid nanopub: {test_file}')
        np_g = ConjunctiveGraph()
        np_g.parse(test_file, format="trix")
        np = Nanopub(
            conf=config_testsuite,
            rdf=np_g
        )
        java_np = java_wrap.sign(np)
        np.sign()
        assert np.has_valid_signature
        assert np.is_valid
        assert np.source_uri == java_np


def test_nanopub_testsuite_valid_signed():
    test_files = [
        "./tests/testsuite/valid/signed/nanopub-python1.trig",
        # "./tests/testsuite/valid/signed/simple1-signed-rsa.trig",
        # "./tests/testsuite/valid/signed/simple1-signed-dsa.trig",
    ]
    # java -jar lib/nanopub-1.38-jar-with-dependencies.jar sign tests/testsuite/transform/signed/rsa-key1/simple1.in.trig

    for test_file in test_files:
        print(f'✅ Testing validating signed valid nanopub: {test_file}')
        np = Nanopub(
            conf=config_testsuite,
            rdf=Path(test_file)
        )
        assert np.is_valid


def test_nanopub_testsuite_invalid():
    test_files = [
        "./tests/testsuite/invalid/plain/emptya.trig",
        "./tests/testsuite/invalid/plain/emptyinfo.trig",
        "./tests/testsuite/invalid/plain/emptyprov.trig",
        "./tests/testsuite/invalid/plain/extragraph.trig",
        "./tests/testsuite/invalid/plain/noinfolink.trig",
        "./tests/testsuite/invalid/plain/noprovlink.trig",
        "./tests/testsuite/invalid/plain/valid_invalid1.trig",
        "./tests/testsuite/invalid/signed/nanopub-index1.trig",
        # ValueError: RSA key format is not supported:
        # "./tests/testsuite/invalid/signed/simple1-invalid-rsa.trig",
    ]
    # java -jar lib/nanopub-1.*-jar-with-dependencies.jar sign tests/testsuite/transform/signed/rsa-key1/simple1.in.trig

    for test_file in test_files:
        print(f'❎ Testing validating signed invalid nanopub: {test_file}')

        try:
            np = Nanopub(
                conf=config_testsuite,
                rdf=Path(test_file)
            )
            np.is_valid
            assert False
        except MalformedNanopubError as e:
            print(e)
            assert True


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
