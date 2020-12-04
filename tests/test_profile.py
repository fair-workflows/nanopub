import pytest
from pathlib import Path
from unittest import mock

from nanopub import profile


def test_load_profile(tmpdir):

    test_file = Path(tmpdir / 'profile.yml')
    with test_file.open('w') as f:
        f.write(
            'orcid_id: pietje\n'
            'name: https://orcid.org/0000-0000-0000-0000\n'
            'public_key: /home/.nanopub/id_rsa.pub\n'
            'private_key: /home/.nanopub/id_rsa\n')

    with mock.patch('nanopub.profile.PROFILE_PATH', test_file):
        profile.get_profile.cache_clear()
        p = profile.get_profile()

        assert p.orcid_id == 'pietje'
        assert p.name == 'https://orcid.org/0000-0000-0000-0000'
        assert p.public_key == Path('/home/.nanopub/id_rsa.pub')
        assert p.private_key == Path('/home/.nanopub/id_rsa')
        assert p.introduction_nanopub_uri is None


def test_fail_loading_incomplete_profile(tmpdir):
    test_file = Path(tmpdir / 'profile.yml')
    with test_file.open('w') as f:
        f.write('orcid_id: pietje\n')

    with mock.patch('nanopub.profile.PROFILE_PATH', test_file):
        profile.get_profile.cache_clear()

        with pytest.raises(profile.ProfileError):
            profile.get_profile()


def test_store_profile(tmpdir):
    test_file = Path(tmpdir / 'profile.yml')

    p = profile.Profile('pietje', 'https://orcid.org/0000-0000-0000-0000',
                        Path('/home/.nanopub/id_rsa.pub'), Path('/home/.nanopub/id_rsa'))

    with mock.patch('nanopub.profile.PROFILE_PATH', test_file):
        profile.store_profile(p)

        with test_file.open('r') as f:
            assert f.read() == (
                'orcid_id: pietje\n'
                'name: https://orcid.org/0000-0000-0000-0000\n'
                'public_key: /home/.nanopub/id_rsa.pub\n'
                'private_key: /home/.nanopub/id_rsa\n'
                'introduction_nanopub_uri:\n')


def test_get_public_key(tmpdir):

    fake_public_key = 'ssh-rsa AAABBBCCC111222333 somemachine@somewhere.nl\n'

    public_key_path = Path(tmpdir / 'id_rsa.pub')
    private_key_path = Path(tmpdir / 'id_rsa')
    p = profile.Profile('pietje', 'https://orcid.org/0000-0000-0000-0000',
                        public_key_path, private_key_path)

    test_profile = Path(tmpdir / 'profile.yml')
    with mock.patch('nanopub.profile.PROFILE_PATH', test_profile):
        profile.store_profile(p)

        # Check for fail if keys are not there
        with pytest.raises(profile.ProfileError):
            profile.get_public_key()

        # Check correct keys are returned if they do exist
        with open(public_key_path, 'w') as outfile:
            outfile.write(fake_public_key)

        assert profile.get_public_key() == fake_public_key


def test_introduction_nanopub_uri_roundtrip(tmpdir):
    test_file = Path(tmpdir / 'profile.yml')

    p = profile.Profile('pietje', 'https://orcid.org/0000-0000-0000-0000',
                        Path('/home/.nanopub/id_rsa.pub'), Path('/home/.nanopub/id_rsa'),
                        'https://example.com/nanopub')

    with mock.patch('nanopub.profile.PROFILE_PATH', test_file):
        profile.store_profile(p)

        with test_file.open('r') as f:
            assert f.read() == (
                'orcid_id: pietje\n'
                'name: https://orcid.org/0000-0000-0000-0000\n'
                'public_key: /home/.nanopub/id_rsa.pub\n'
                'private_key: /home/.nanopub/id_rsa\n'
                'introduction_nanopub_uri: https://example.com/nanopub\n')

        profile.get_profile.cache_clear()
        p2 = profile.get_profile()
        assert p.orcid_id == p2.orcid_id
        assert p.name == p2.name
        assert p.public_key == p2.public_key
        assert p.private_key == p2.private_key
        assert p.introduction_nanopub_uri == p2.introduction_nanopub_uri
