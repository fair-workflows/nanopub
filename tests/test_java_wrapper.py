import shutil
from pathlib import Path

import pytest

from nanopub import java_wrapper
from nanopub.definitions import TEST_RESOURCES_FILEPATH

NANOPUB_SAMPLE_SIGNED = TEST_RESOURCES_FILEPATH / 'nanopub_sample_signed.trig'
NANOPUB_SAMPLE_UNSIGNED = TEST_RESOURCES_FILEPATH / 'nanopub_sample_unsigned.trig'


def test_extract_nanopub_url_from_namespace():
    url = java_wrapper.extract_nanopub_url(NANOPUB_SAMPLE_SIGNED)

    target_url = 'http://purl.org/np/RAzPytdERsBd378zHGvwgRbat1MCiS7QrxNrPxe9yDu6E'
    assert target_url == url


def test_sign_nanopub_creates_file(tmp_path):
    # Work in temporary dir so resulting files do not end up in repo
    temp_unsigned_file = tmp_path / 'unsigned.trig'
    shutil.copy(NANOPUB_SAMPLE_UNSIGNED, temp_unsigned_file)

    signed_file = java_wrapper.sign(unsigned_file=temp_unsigned_file)

    assert Path(signed_file).exists()


def test_sign_fails_on_invalid_nanopub(tmp_path):
    invalid_file = tmp_path / 'invalid.trig'
    invalid_file.write_text('this file is invalid')

    with pytest.raises(Exception):
        java_wrapper.sign(invalid_file)
