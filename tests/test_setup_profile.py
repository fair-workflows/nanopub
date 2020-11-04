from pathlib import Path
from unittest.mock import patch

import pytest

from nanopub import setup_profile
from nanopub.setup_profile import validate_orcid_id

MOCK_PUBLIC_KEY = 'this is not a real rsa public key'
MOCK_PRIVATE_KEY = 'this is not a real rsa private key'
PUBLIC_KEYFILE = 'id_rsa.pub'
PRIVATE_KEYFILE = 'id_rsa'
NANOPUB_DIR = '.nanopub'

ORCID = '123'
NAME = 'pietje'
PUBLISH = False


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

    with patch('nanopub.setup_profile.USER_CONFIG_DIR', nanopub_path), \
         patch('nanopub.setup_profile.DEFAULT_PUBLIC_KEY_PATH', new_public_keyfile), \
         patch('nanopub.setup_profile.DEFAULT_PRIVATE_KEY_PATH', new_private_keyfile):

        setup_profile.main(args=['--keypair', str(custom_public_key_path), str(custom_private_key_path), '--name',
                                 NAME, '--orcid', ORCID, '--no-publish'], standalone_mode=False)

    nanopub_path = mock_homedir / NANOPUB_DIR

    new_public_keyfile = nanopub_path / PUBLIC_KEYFILE
    new_private_keyfile = nanopub_path / PRIVATE_KEYFILE

    assert new_public_keyfile.exists()
    assert new_public_keyfile.read_text() == MOCK_PUBLIC_KEY
    assert new_private_keyfile.exists()
    assert new_private_keyfile.read_text() == MOCK_PRIVATE_KEY


def test_validate_orcid_id():
    valid_ids = ['1234-5678-1234-5678', '']
    for orcid_id in valid_ids:
        validate_orcid_id(ctx=None, orcid_id=orcid_id)
    invalid_ids = ['abcd-efgh-abcd-efgh', '1234-5678-1234-567', '1234-5678-1234-56789']
    for orcid_id in invalid_ids:
        with pytest.raises(ValueError):
            validate_orcid_id(ctx=None, orcid_id=orcid_id)
