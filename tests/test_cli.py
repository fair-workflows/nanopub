from pathlib import Path
from unittest.mock import MagicMock

import pytest
from nanopub_testsuite_connector import TestSuiteSubfolder
from rdflib import Dataset, URIRef
from typer.testing import CliRunner

from nanopub import namespaces
from nanopub.__main__ import cli
from nanopub._version import __version__
from nanopub.definitions import DEFAULT_PROFILE_PATH
from nanopub.profile import _validate_agent_id, ProfileError
from nanopub.utils import MalformedNanopubError

runner = CliRunner()


def test_validate_agent_id():
    # Any URI is accepted at face value, including non-ORCID identities and bare
    # ORCID identifiers (expanded later by the Profile).
    accepted = ['https://orcid.org/0000-0000-0000-0001',
                'https://orcid.org/1234-5678-1234-5673',
                'https://orcid.org/0000-0000-0000-001X',
                'https://other-url.org/1234-5678-1234-5678',
                'https://example.org/agent/42',
                'https://orcid.org/0000-0000-0000-0000',
                ]
    for agent_id in accepted:
        assert _validate_agent_id(agent_id=agent_id) == agent_id

    # Only values that claim to be an ORCID but are malformed are rejected.
    invalid_orcids = [
        'https://orcid.org/abcd-efgh-abcd-efgh',  # invalid format
        'https://orcid.org/0000-0003-4112-6826',  # invalid checksum
        'https://orcid.org/',  # invalid checksum
        'https://orcid.org/1234-5678-1234-5678',  # invalid checksum
        'https://orcid.org/1234-5678-1234-56789',  # too long
        'https://orcid.org/abcd-efgh-abcd-efgh',
        'https://orcid.org/1234-5678-1234-567',
    ]
    for agent_id in invalid_orcids:
        with pytest.raises(ProfileError):
            _validate_agent_id(agent_id=agent_id)


def test_setup():
    # np setup --orcid-id https://orcid.org/0000-0000-0000-0000 --name "Python test" --newkeys --no-publish
    result = runner.invoke(cli, [
        "setup",
        "--orcid-id", "https://orcid.org/0000-0000-0000-0001",
        "--name", "Python test",
        "--newkeys", "--no-publish"
    ])
    assert result.exit_code == 1
    assert "Setting up nanopub profile" in result.stdout
    assert Path(DEFAULT_PROFILE_PATH).exists()


def test_profile():
    result = runner.invoke(cli, [
        "profile",
    ])
    assert "User profile in" in result.stdout


def test_publish(testsuite):
    test_file = str(testsuite.get_valid(TestSuiteSubfolder.PLAIN)[0].path)
    result = runner.invoke(cli, [
        "publish", test_file, "--test"
    ])
    assert result.exit_code == 0
    assert "Nanopub published at" in result.stdout


def test_sign_with_key(testsuite):
    tc = testsuite.get_transform_cases()[0]
    test_file = str(tc.plain.path)
    private_key = str(testsuite.get_signing_key(tc.key_name).private_key)
    result = runner.invoke(cli, [
        "sign", test_file,
        "-k", private_key,
    ])
    assert result.exit_code == 0
    assert "Nanopub signed in" in result.stdout


def test_sign_with_orcid(testsuite, tmp_path):
    """A bare ORCID passed to --orcid is normalized and recorded as signedBy."""
    tc = testsuite.get_transform_cases()[0]
    test_file = tmp_path / "to_sign.trig"
    test_file.write_text(tc.plain.path.read_text())
    private_key = str(testsuite.get_signing_key(tc.key_name).private_key)

    result = runner.invoke(cli, [
        "sign", str(test_file),
        "-k", private_key,
        "-o", "1234-5678-1234-5673",
    ])

    assert result.exit_code == 0
    signed = tmp_path / "signed.to_sign.trig"
    assert signed.exists()
    ds = Dataset()
    ds.parse(signed, format="trig")
    signed_by = {o for _, _, o, _ in ds.quads((None, namespaces.NPX.signedBy, None, None))}
    assert URIRef("https://orcid.org/1234-5678-1234-5673") in signed_by


def test_version():
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert __version__ == result.stdout.strip()


def test_setup_with_keypair(monkeypatch, tmp_path):
    monkeypatch.setattr("nanopub.__main__._rsa_keys_exist", lambda: False)
    monkeypatch.setattr("nanopub.__main__.generate_keyfiles", lambda path: None)
    mock_np = MagicMock()
    monkeypatch.setattr("nanopub.__main__.NanopubIntroduction", lambda **kw: mock_np)

    pub_key = tmp_path / "pub.pem"
    priv_key = tmp_path / "priv.pem"
    pub_key.write_text("pub")
    priv_key.write_text("priv")

    result = runner.invoke(cli, [
        "setup",
        "--orcid-id", "https://orcid.org/0000-0000-0000-0001",
        "--name", "Python test",
        "--keypair", str(pub_key), str(priv_key),
        "--no-publish"
    ])
    assert "Introduction Nanopub signed but not published" in result.output
    mock_np.sign.assert_called_once()
    mock_np.publish.assert_not_called()


def test_setup_publish_yes(monkeypatch):
    monkeypatch.setattr("nanopub.__main__._rsa_keys_exist", lambda: False)
    monkeypatch.setattr("nanopub.__main__.generate_keyfiles", lambda path: None)

    monkeypatch.setattr("typer.prompt", lambda prompt, type=str, default=None: "y")

    mock_np = MagicMock()
    monkeypatch.setattr("nanopub.__main__.NanopubIntroduction", lambda **kw: mock_np)

    result = runner.invoke(cli, [
        "setup",
        "--orcid-id", "https://orcid.org/0000-0000-0000-0001",
        "--name", "Python test",
        "--newkeys"
    ])
    assert "Introduction Nanopub published" in result.output
    mock_np.sign.assert_called_once()
    mock_np.publish.assert_called_once()


def test_setup_publish_no(monkeypatch):
    monkeypatch.setattr("nanopub.__main__._rsa_keys_exist", lambda: False)
    monkeypatch.setattr("nanopub.__main__.generate_keyfiles", lambda path: None)

    monkeypatch.setattr("typer.prompt", lambda prompt, type=str, default=None: "n")

    mock_np = MagicMock()
    monkeypatch.setattr("nanopub.__main__.NanopubIntroduction", lambda **kw: mock_np)

    result = runner.invoke(cli, [
        "setup",
        "--orcid-id", "https://orcid.org/0000-0000-0000-0001",
        "--name", "Python test",
        "--newkeys"
    ])
    assert "Introduction Nanopub signed but not published" in result.output
    mock_np.sign.assert_called_once()
    mock_np.publish.assert_not_called()


def test_profile_error(monkeypatch):
    monkeypatch.setattr(
        "nanopub.__main__.load_profile",
        lambda: (_ for _ in ()).throw(Exception("Profile error"))
    )

    result = runner.invoke(cli, ["profile"])
    assert result.exception is not None
    assert "Profile error" in str(result.exception)


def test_sign_without_key(monkeypatch, testsuite):
    mock_np = MagicMock()
    monkeypatch.setattr("nanopub.__main__.Nanopub", lambda **kw: mock_np)
    test_file = str(testsuite.get_valid(TestSuiteSubfolder.PLAIN)[0].path)

    result = runner.invoke(cli, ["sign", test_file])
    assert result.exit_code == 0
    mock_np.sign.assert_called_once()


def test_sign_error(monkeypatch, testsuite):
    mock_np = MagicMock()
    mock_np.sign.side_effect = Exception("Signing failed")
    monkeypatch.setattr("nanopub.__main__.Nanopub", lambda **kw: mock_np)
    tc = testsuite.get_transform_cases()[0]
    test_file = str(tc.plain.path)
    private_key = str(testsuite.get_signing_key(tc.key_name).private_key)

    result = runner.invoke(cli, ["sign", test_file, "-k", private_key])
    assert result.exception is not None
    assert "Signing failed" in str(result.exception)


def test_publish_error(monkeypatch, testsuite):
    mock_np = MagicMock()
    mock_np.publish.side_effect = Exception("Publish failed")
    monkeypatch.setattr("nanopub.__main__.Nanopub", lambda **kw: mock_np)
    test_file = str(testsuite.get_valid(TestSuiteSubfolder.PLAIN)[0].path)

    result = runner.invoke(cli, ["publish", test_file, "--test"])
    assert result.exception is not None
    assert "Publish failed" in str(result.exception)


def test_check_valid(monkeypatch, testsuite):
    mock_np = MagicMock()
    type(mock_np).is_valid = True
    monkeypatch.setattr("nanopub.__main__.Nanopub", lambda **kw: mock_np)
    test_file = str(testsuite.get_valid(TestSuiteSubfolder.PLAIN)[0].path)

    result = runner.invoke(cli, ["check", test_file])
    assert "Valid nanopub" in result.output


def test_check_invalid(monkeypatch, testsuite):
    mock_np = MagicMock()
    type(mock_np).is_valid = property(lambda self: (_ for _ in ()).throw(MalformedNanopubError("Malformed")))
    monkeypatch.setattr("nanopub.__main__.Nanopub", lambda **kw: mock_np)
    test_file = str(testsuite.get_valid(TestSuiteSubfolder.PLAIN)[0].path)

    result = runner.invoke(cli, ["check", test_file])
    assert "Invalid nanopub" in result.output
