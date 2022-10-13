# from functools import lru_cache
from base64 import decodebytes
from pathlib import Path
from typing import Optional, Union

import yatiml
from Crypto.PublicKey import RSA

from nanopub.definitions import DEFAULT_PROFILE_PATH, USER_CONFIG_DIR, log

PROFILE_INSTRUCTIONS_MESSAGE = '''
    Follow these instructions to correctly setup your nanopub profile:
    https://nanopub.readthedocs.io/en/latest/getting-started/setup.html#setup-your-profile
'''


class ProfileError(RuntimeError):
    """
    Error to be raised if profile is not setup correctly.
    """


class Profile:
    """Represents a user profile.

    Attributes:
        orcid_id: The user's ORCID
        name: The user's name
        public_key: Path to the user's public key or string
        private_key: Path to the user's private key or string
        introduction_nanopub_uri: URI of the user's profile nanopub
    """

    def __init__(
            self,
            orcid_id: str,
            name: str,
            private_key: Union[Path, str],
            public_key: Optional[Union[Path, str]] = None,
            introduction_nanopub_uri: Optional[str] = None
    ) -> None:
        """Create a Profile."""
        self._orcid_id = orcid_id
        self._name = name
        self._introduction_nanopub_uri = introduction_nanopub_uri

        if isinstance(private_key, Path):
            try:
                with open(private_key) as f:
                    self._private_key = f.read().strip()
            except FileNotFoundError:
                raise ProfileError(
                    f'Private key file {private_key} for nanopub not found.\n'
                    f'Maybe your nanopub profile was not set up yet or not set up '
                    f'correctly. \n{PROFILE_INSTRUCTIONS_MESSAGE}'
                )
        else:
            self._private_key = private_key

        if not public_key:
            log.info('Public key not provided when loading the Nanopub profile, generating it from the provided private key')
            key = RSA.importKey(decodebytes(self._private_key.encode()))
            self._public_key = key.publickey().export_key().decode('utf-8')
        else:
            if isinstance(public_key, Path):
                try:
                    with open(public_key) as f:
                        self._public_key = f.read().strip()
                except FileNotFoundError:
                    raise ProfileError(
                        f'Private key file {public_key} for nanopub not found.\n'
                        f'Maybe your nanopub profile was not set up yet or not set up '
                        f'correctly. \n{PROFILE_INSTRUCTIONS_MESSAGE}'
                    )
            else:
                self._public_key = public_key



    @property
    def orcid_id(self):
        return self._orcid_id

    @orcid_id.setter
    def orcid_id(self, value):
        self._orcid_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def private_key(self):
        return self._private_key

    @private_key.setter
    def private_key(self, value):
        self._private_key = value

    @property
    def public_key(self):
        return self._public_key

    @public_key.setter
    def public_key(self, value):
        self._public_key = value

    @property
    def introduction_nanopub_uri(self):
        return self._introduction_nanopub_uri

    @introduction_nanopub_uri.setter
    def introduction_nanopub_uri(self, value):
        self._introduction_nanopub_uri = value



    # TODO: remove?
    def get_public_key(self) -> str:
        """Returns the user's public key."""
        return self._public_key

    def get_private_key(self) -> str:
        """Returns the user's private key."""
        return self._private_key

    def __repr__(self):
        return f"""ORCID: {self._orcid_id}
Name: {self._name}
Private key: {self._private_key}
Public key: {self._public_key}
Intro Nanopub URI: {self._introduction_nanopub_uri}
"""


class ProfileLoader(Profile):
    """A class to load a user profile from a local YAML file, only used for YAtiML."""
    def __init__(
            self,
            orcid_id: str,
            name: str,
            private_key: Path,
            public_key: Optional[Path],
            introduction_nanopub_uri: Optional[str] = None
    ) -> None:
        """Create a Profile."""
        super().__init__(
            orcid_id=orcid_id,
            name=name,
            private_key=private_key,
            public_key=public_key,
            introduction_nanopub_uri=introduction_nanopub_uri,
        )


_load_profile = yatiml.load_function(ProfileLoader)


_dump_profile = yatiml.dump_function(ProfileLoader)


# TODO: remove
def get_orcid_id() -> str:
    """Returns the user's ORCID."""
    return load_profile().orcid_id


# @lru_cache()
def load_profile(profile_path: Union[Path, str] = DEFAULT_PROFILE_PATH) -> Profile:
    """Retrieve nanopub user profile.

    By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Returns:
        A Profile containing the data from the configuration file.

    Raises:
        yatiml.RecognitionError: If there is an error in the file.
    """
    try:
        return _load_profile(Path(profile_path))
    except (yatiml.RecognitionError, FileNotFoundError) as e:
        msg = (f'{e}\nYour nanopub profile has not been set up yet, or is not set up correctly.\n'
               f'{PROFILE_INSTRUCTIONS_MESSAGE}')
        raise ProfileError(msg)


# TODO: fix for new Profile class
def store_profile(profile: Profile, folder: Path) -> Path:
    """Stores the nanopub user profile.

    By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Args:
        profile: The profile to store as the user's profile.

    Returns:
        The path where the profile was stored.

    Raises:
        yatiml.RecognitionError: If there is an error in the file.
    """
    pdump = ProfileLoader(
        name=profile.name,
        orcid_id=profile.orcid_id,
        private_key=folder / "id_rsa",
        public_key=folder / "id_rsa.pub",
        introduction_nanopub_uri=profile.introduction_nanopub_uri,
    )
    _dump_profile(pdump, folder / "profile.yml")
    return folder / "profile.yml"


def generate_keys(path: Path = USER_CONFIG_DIR) -> str:
    """Generate private/public RSA key pair at the path specified in the profile.yml, to be used to sign nanopubs"""
    if not path.exists():
        path.mkdir()

    key = RSA.generate(2048)
    private_key_str = key.export_key('PEM', pkcs=8).decode('utf-8')
    public_key_str = key.publickey().export_key().decode('utf-8')

    # Format private and public keys to remove header/footer and all newlines, as this is required by nanopub-java
    private_key_str = private_key_str.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").replace("\n", "").strip()
    public_key_str = public_key_str.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "").strip()
    private_path = path / "id_rsa"
    public_path = path / "id_rsa.pub"

    # Store key pair
    private_key_file = open(private_path, "w")
    private_key_file.write(private_key_str)
    private_key_file.close()

    public_key_file = open(public_path, "w")
    public_key_file.write(public_key_str)
    public_key_file.close()
    log.info(f"Public/private RSA key pair has been generated in {private_path} and {public_path}")
    return public_key_str
