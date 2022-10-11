import os
from pathlib import Path
from unittest import mock

import pytest

from tests.conftest import test_profile_path
from nanopub.profile import Profile, load_profile, ProfileError
from nanopub.definitions import TEST_RESOURCES_FILEPATH

TEST_PRIVATE_KEY = 'MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCjY1gsFxmak6SOCouJPuEzHNForkqFhgfHE3aAIAx+Y5q6UDEDM9Q0EksheNffJB4iPqsAfiFpY0ARQY92K5r8P4+a78eu9reYrb2WxZb1qPJmvR7XZ6sN1oHD7dd/EyQoJmQsmOKdrqaLRbzR7tZrf52yvKkwNWXcIVhW8uxe7iUgxiojZpW9srKoK/qFRpaUZSKn7Z/zgtDH9FJkYbBsGPDMqp78Kzt+sJb+U2W+wCSSy34jIUxx6QRbzvn6uexc/emFw/1DU5y7zBudhgC7mVk8vX1gUNKyjZBzlOmRcretrANgffqs5fx/TMHN1xtkA/H1u1IKBfKoyk/xThMLAgMBAAECggEAECuG0GZA3HF8OaqFgMG+W+agOvH04h4Pqv4cHjYNxnxpFcNV9nEssTKWSOvCwYy7hrwZBGV3PQzbjFmmrxVFs20+8yCD7KbyKKQZPVC0zf84bj6NTNgvr6DpGtDxINxuGaMjCt7enqhoRyRRuZ0fj2gD3Wqae/Ds8cpDCefkyMg0TvauHSUj244vGq5nt93txUv1Sa+/8tWZ77Dm0s5a3wUYB2IeAMl5WrO2GMvgzwH+zT+4kvNWg5S0Ze4KE+dG3lSIYZjo99h14LcQS9eALC/VBcAJ6pRXaCTT/TULtcLNeOpoc9Fu25f0yTsDt6Ga5ApliYkb7rDhV+OFrw1sYQKBgQDCE9so+dPg7qbp0cV+lbb7rrV43m5s9Klq0riS7u8m71oTwhmvm6gSLfjzqb8GLrmflCK4lKPDSTdwyvd+2SSmOXySw94zr1Pvc7sHdmMRyA7mH3m+zSOOgyCTTKyhDRCNcRIkysoL+DecDhNo4Fumf71tsqDYogfxpAQhn0re8wKBgQDXhMmmT2oXiMnYHhi2k7CJe3HUqkZgmW4W44SWqKHp0V6sjcHm0N0RT5Hz1BFFUd5Y0ZB3JLcah19myD1kKYCj7xz6oVLb8O7LeAZNlb0FsrtD7NU+Hciywo8qESiA7UYDkU6+hsmxaI01DsttMIdG4lSBbEjA7t4IQC5lyr7xiQKBgQCN87YGJ40Y5ZXCSgOZDepz9hqX2KGOIfnUv2HvXsIfiUwqTXs6HbD18xg3KL4myIBOvywSM+4ABYp+foY+Cpcq2btLIeZhiWjsKIrw71+Q/vIe0YDb1PGf6DsoYhmWBpdHzR9HN+hGjvwlsYny2L9Qbfhgxxmsuf7zeFLpQLijjwKBgH7TD28k8IOk5VKec2CNjKd600OYaA3UfCpP/OhDl/RmVtYoHWDcrBrRvkvEEd2/DZ8qw165Zl7gJs3vK+FTYvYVcfIzGPWA1KU7nkntwewmf3i7V8lT8ZTwVRsmObWU60ySJ8qKuwoBQodki2VX12NpMN1wgWe3qUUlr6gLJU4xAoGAet6nD3QKwk6TTmcGVfSWOzvpaDEzGkXjCLaxLKh9GreM/OE+h5aN2gUoFeQapG5rUwI/7Qq0xiLbRXw+OmfAoV2XKv7iI8DjdIh0F06mlEAwQ/B0CpbqkuuxphIbchtdcz/5ra233r3BMNIqBl3VDDVoJlgHPg9msOTRy13lFqc='
TEST_PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAo2NYLBcZmpOkjgqLiT7hMxzRaK5KhYYHxxN2gCAMfmOaulAxAzPUNBJLIXjX3yQeIj6rAH4haWNAEUGPdiua/D+Pmu/Hrva3mK29lsWW9ajyZr0e12erDdaBw+3XfxMkKCZkLJjina6mi0W80e7Wa3+dsrypMDVl3CFYVvLsXu4lIMYqI2aVvbKyqCv6hUaWlGUip+2f84LQx/RSZGGwbBjwzKqe/Cs7frCW/lNlvsAkkst+IyFMcekEW875+rnsXP3phcP9Q1Ocu8wbnYYAu5lZPL19YFDSso2Qc5TpkXK3rawDYH36rOX8f0zBzdcbZAPx9btSCgXyqMpP8U4TCwIDAQAB'


def test_instantiate_profile_path():
    p = Profile(
        name='Python Tests',
        orcid_id='https://orcid.org/0000-0000-0000-0000',
        private_key=Path(os.path.join(TEST_RESOURCES_FILEPATH, "id_rsa")),
        public_key=Path(os.path.join(TEST_RESOURCES_FILEPATH, "id_rsa.pub"))
    )

    assert p.orcid_id == 'https://orcid.org/0000-0000-0000-0000'
    assert p.name == 'Python Tests'
    assert p.introduction_nanopub_uri is None
    assert p.private_key == TEST_PRIVATE_KEY
    assert p.public_key == TEST_PUBLIC_KEY
    assert p.get_private_key() == TEST_PRIVATE_KEY
    assert p.get_public_key() == TEST_PUBLIC_KEY


def test_instantiate_profile_str():
    p = Profile(
        name='Python Tests',
        orcid_id='https://orcid.org/0000-0000-0000-0000',
        private_key=TEST_PRIVATE_KEY,
        public_key=TEST_PUBLIC_KEY
    )

    assert p.orcid_id == 'https://orcid.org/0000-0000-0000-0000'
    assert p.name == 'Python Tests'
    assert p.introduction_nanopub_uri is None
    assert p.private_key == TEST_PRIVATE_KEY
    assert p.public_key == TEST_PUBLIC_KEY
    assert p.get_private_key() == TEST_PRIVATE_KEY
    assert p.get_public_key() == TEST_PUBLIC_KEY



def test_load_profile():
    p = load_profile(test_profile_path)

    assert p.orcid_id == 'https://orcid.org/0000-0000-0000-0000'
    assert p.name == 'Python Tests'
    assert p.introduction_nanopub_uri is None
    assert p.private_key == TEST_PRIVATE_KEY
    assert p.public_key == TEST_PUBLIC_KEY
    assert p.get_private_key() == TEST_PRIVATE_KEY
    assert p.get_public_key() == TEST_PUBLIC_KEY


def test_fail_loading_incomplete_profile(tmpdir):
    test_file = Path(tmpdir / 'profile.yml')
    profile_yaml = f"""orcid_id: https://orcid.org/0000-0000-0000-0000
name: Python Tests"""
    with open(test_file, "w") as f:
        f.write(profile_yaml)

    with pytest.raises(ProfileError):
            p = load_profile(test_file)


def test_profile_file_not_found(tmpdir):
    test_file = Path(tmpdir / 'profile.yml')
    with pytest.raises(ProfileError):
        p = load_profile(test_file)






# def test_store_profile(tmpdir):
#     test_file = Path(tmpdir / 'profile.yml')

#     p = profile.Profile('pietje', 'https://orcid.org/0000-0000-0000-0000',
#                         Path('/home/.nanopub/id_rsa.pub'), Path('/home/.nanopub/id_rsa'))

#     with mock.patch('nanopub.profile.PROFILE_PATH', test_file):
#         profile.store_profile(p)

#         with test_file.open('r') as f:
#             assert f.read() == (
#                 'orcid_id: pietje\n'
#                 'name: https://orcid.org/0000-0000-0000-0000\n'
#                 f"public_key: {Path('/home/.nanopub/id_rsa.pub')}\n"
#                 f"private_key: {Path('/home/.nanopub/id_rsa')}\n"
#                 'introduction_nanopub_uri:\n')


# def test_get_public_key(tmpdir):

#     fake_public_key = 'AAABBBCCC111222333\n'

#     public_key_path = Path(tmpdir / 'id_rsa.pub')
#     private_key_path = Path(tmpdir / 'id_rsa')
#     p = profile.Profile('pietje', 'https://orcid.org/0000-0000-0000-0000',
#                         public_key_path, private_key_path)

#     test_profile = Path(tmpdir / 'profile.yml')
#     with mock.patch('nanopub.profile.PROFILE_PATH', test_profile):
#         profile.store_profile(p)

#         # Check for fail if keys are not there
#         with pytest.raises(profile.ProfileError):
#             p.get_public_key()

#         # Check correct keys are returned if they do exist
#         with open(public_key_path, 'w') as outfile:
#             outfile.write(fake_public_key)

#         assert p.get_public_key() == fake_public_key


# def test_introduction_nanopub_uri_roundtrip(tmpdir):
#     test_file = Path(tmpdir / 'profile.yml')

#     p = profile.Profile('pietje', 'https://orcid.org/0000-0000-0000-0000',
#                         Path('/home/.nanopub/id_rsa.pub'), Path('/home/.nanopub/id_rsa'),
#                         'https://example.com/nanopub')

#     with mock.patch('nanopub.profile.PROFILE_PATH', test_file):
#         profile.store_profile(p)

#         with test_file.open('r') as f:
#             assert f.read() == (
#                 'orcid_id: pietje\n'
#                 'name: https://orcid.org/0000-0000-0000-0000\n'
#                 f"public_key: {Path('/home/.nanopub/id_rsa.pub')}\n"
#                 f"private_key: {Path('/home/.nanopub/id_rsa')}\n"
#                 'introduction_nanopub_uri: https://example.com/nanopub\n')

#         profile.get_profile.cache_clear()
#         p2 = profile.get_profile()
#         assert p.orcid_id == p2.orcid_id
#         assert p.name == p2.name
#         assert p.public_key == p2.public_key
#         assert p.private_key == p2.private_key
#         assert p.introduction_nanopub_uri == p2.introduction_nanopub_uri
