from pathlib import Path
from unittest.mock import patch

import pytest
import rdflib

from nanopub import __main__
from nanopub.__main__ import validate_orcid_id

MOCK_PUBLIC_KEY = 'this is not a real rsa public key'
MOCK_PRIVATE_KEY = 'this is not a real rsa private key'
PUBLIC_KEYFILE = 'id_rsa.pub'
PRIVATE_KEYFILE = 'id_rsa'
NANOPUB_DIR = '.nanopub'

TEST_ORCID_ID = 'https://orcid.org/0000-0000-0000-0000'
NAME = 'pietje'


def test_provided_keypair_copied_to_nanopub_dir(tmp_path: Path):
    mock_homedir = tmp_path / 'home'
    mock_otherdir = tmp_path / 'other'

    mock_homedir.mkdir()
    mock_otherdir.mkdir()

    custom_public_key_path = mock_otherdir / PUBLIC_KEYFILE
    custom_private_key_path = mock_otherdir / PRIVATE_KEYFILE

    # Store keys in custom path
    custom_public_key_path.write_text(MOCK_PUBLIC_KEY)
    custom_private_key_path.write_text(MOCK_PRIVATE_KEY)

    nanopub_path = mock_homedir / NANOPUB_DIR

    new_public_keyfile = nanopub_path / PUBLIC_KEYFILE
    new_private_keyfile = nanopub_path / PRIVATE_KEYFILE

    with patch('nanopub.setup_nanopub_profile.USER_CONFIG_DIR', nanopub_path), \
            patch('nanopub.setup_nanopub_profile.DEFAULT_PUBLIC_KEY_PATH', new_public_keyfile), \
            patch('nanopub.setup_nanopub_profile.DEFAULT_PRIVATE_KEY_PATH', new_private_keyfile), \
            patch('nanopub.profile.PROFILE_PATH', nanopub_path / 'profile.yml'), \
            patch('nanopub.setup_nanopub_profile.NanopubClient.publish') as mocked_client_publish:
        __main__.cli(
            args=['--keypair', str(custom_public_key_path), str(custom_private_key_path),
                  '--name',  NAME,
                  '--orcid_id', TEST_ORCID_ID,
                  '--publish'],
            standalone_mode=False)

    nanopub_path = mock_homedir / NANOPUB_DIR

    new_public_keyfile = nanopub_path / PUBLIC_KEYFILE
    new_private_keyfile = nanopub_path / PRIVATE_KEYFILE

    assert new_public_keyfile.exists()
    assert new_public_keyfile.read_text() == MOCK_PUBLIC_KEY
    assert new_private_keyfile.exists()
    assert new_private_keyfile.read_text() == MOCK_PRIVATE_KEY

    # Check that intro nanopub was 'published'
    assert mocked_client_publish.called


def test_no_keypair_provided(tmp_path: Path):
    mock_homedir = tmp_path / 'home'
    mock_homedir.mkdir()
    nanopub_path = mock_homedir / NANOPUB_DIR

    new_public_keyfile = nanopub_path / PUBLIC_KEYFILE
    new_private_keyfile = nanopub_path / PRIVATE_KEYFILE
    new_default_keys_path_prefix = nanopub_path / 'id'

    with patch(
            'nanopub.setup_nanopub_profile.USER_CONFIG_DIR',
            nanopub_path), \
         patch(
            'nanopub.setup_nanopub_profile.DEFAULT_PUBLIC_KEY_PATH',
            new_public_keyfile), \
         patch(
            'nanopub.setup_nanopub_profile.DEFAULT_PRIVATE_KEY_PATH',
            new_private_keyfile), \
         patch(
            'nanopub.setup_nanopub_profile.DEFAULT_KEYS_PATH_PREFIX',
            new_default_keys_path_prefix), \
         patch(
            'nanopub.profile.PROFILE_PATH',
            nanopub_path / 'profile.yml'):

        # Call function directly, otherwise click's prompts get in the way
        __main__.cli.callback(TEST_ORCID_ID, False, True, NAME, keypair=None)

        assert new_public_keyfile.exists()
        assert new_private_keyfile.exists()


def test_create_this_is_me_rdf():
    rdf, _ = __main__._create_this_is_me_rdf(TEST_ORCID_ID, 'public key', 'name')
    assert (None, None, rdflib.URIRef(TEST_ORCID_ID)) in rdf


def test_validate_orcid_id():
    valid_ids = ['https://orcid.org/1234-5678-1234-5678',
                 'https://orcid.org/1234-5678-1234-567X']
    for orcid_id in valid_ids:
        assert validate_orcid_id(ctx=None, param=None, orcid_id=orcid_id) == orcid_id

    invalid_ids = ['https://orcid.org/abcd-efgh-abcd-efgh',
                   'https://orcid.org/1234-5678-1234-567',
                   'https://orcid.org/1234-5678-1234-56789',
                   'https://other-url.org/1234-5678-1234-5678',
                   '0000-0000-0000-0000']
    for orcid_id in invalid_ids:
        with pytest.raises(ValueError):
            validate_orcid_id(ctx=None, param=None, orcid_id=orcid_id)
