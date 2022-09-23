import pytest
import requests

from nanopub.client import NANOPUB_TEST_GRLC_URL


def pytest_addoption(parser):
    parser.addoption('--no_rsa_key', action='store_true', default=False,
                     help="enable no_rsa_key decorated tests")


def pytest_configure(config):
    if not config.option.no_rsa_key:
        setattr(config.option, 'markexpr', 'not no_rsa_key')


skip_if_nanopub_server_unavailable = (
    pytest.mark.skipif(requests.get(NANOPUB_TEST_GRLC_URL).status_code != 200,
                       reason='Nanopub server is unavailable'))
