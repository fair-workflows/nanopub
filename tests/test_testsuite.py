from pathlib import Path

from rdflib import ConjunctiveGraph

from nanopub import Nanopub, NanopubConf
from nanopub.utils import MalformedNanopubError
from tests.conftest import java_wrap, profile_test

config_testsuite = NanopubConf(
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=False,
    attribute_publication_to_profile=False,
    profile=profile_test,
    use_test_server=True,
)


def test_testsuite_sign_valid_plain():
    test_files = Path("./tests/testsuite/valid/plain").rglob('*')

    for test_file in test_files:
        print(f'✒️ Testing signing valid plain nanopub: {test_file}')
        if "/signed." in str(test_file):
            continue

        np_g = ConjunctiveGraph()
        if str(test_file).endswith(".xml"):
            np_g.parse(test_file, format="trix")
        else:
            np_g.parse(test_file)

        np = Nanopub(
            conf=config_testsuite,
            rdf=np_g
        )
        # java_np = java_wrap.sign(np)
        # np.sign()
        print(np)
        # assert np.has_valid_signature
        assert np.is_valid
        # assert np.source_uri == java_np


def test_testsuite_sign_valid():
    # TODO: remove
    test_files = [
        # "./tests/testsuite/transform/signed/rsa-key1/simple1.in.trig",
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


def test_testsuite_sign_valid_trix():
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


def test_testsuite_valid_signed():
    test_files = [
        "./tests/testsuite/valid/signed/simple1-signed-rsa.trig",
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


def test_testsuite_invalid():
    test_files = [
        "./tests/testsuite/invalid/plain/emptya.trig",
        "./tests/testsuite/invalid/plain/emptyinfo.trig",
        "./tests/testsuite/invalid/plain/emptyprov.trig",
        "./tests/testsuite/invalid/plain/extragraph.trig",
        "./tests/testsuite/invalid/plain/noinfolink.trig",
        "./tests/testsuite/invalid/plain/noprovlink.trig",
        "./tests/testsuite/invalid/plain/valid_invalid1.trig",
        # "aaa",
        # "aaa",
        # "aaa",
        # "aaa",
        # "aaa",
        # "aaa",
        # "aaa",
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
