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
        assert p.nanopub_uri is None


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
                    'private_key: /home/.nanopub/id_rsa\n')


def test_nanopub_uri_roundtrip(tmpdir):
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
                    'profile_nanopub: https://example.com/nanopub\n')

        profile.get_profile.cache_clear()
        p2 = profile.get_profile()
        assert p.orcid_id == p2.orcid_id
        assert p.name == p2.name
        assert p.public_key == p2.public_key
        assert p.private_key == p2.private_key
        assert p.nanopub_uri == p2.nanopub_uri
