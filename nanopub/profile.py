from functools import lru_cache
from pathlib import Path
from typing import Optional

import yatiml

from nanopub.definitions import PROFILE_PATH

PROFILE_INSTRUCTIONS_MESSAGE = '''
    Follow these instructions to correctly setup your nanopub profile:
    https://nanopub.readthedocs.io/en/latest/getting-started/setup.html#setup-your-profile
'''


class ProfileError(RuntimeError):
    """
    Error to be raised if profile is not setup correctly.
    """
    pass


class Profile:
    """Represents a user profile.

    Attributes:
        orcid_id: The user's ORCID
        name: The user's name
        public_key: Path to the user's public key
        private_key: Path to the user's private key
        introduction_nanopub_uri: URI of the user's profile nanopub
    """

    def __init__(
            self,
            orcid_id: str, name: str,
            public_key: Path, private_key: Path,
            introduction_nanopub_uri: Optional[str] = None
    ) -> None:
        """Create a Profile."""
        self.orcid_id = orcid_id
        self.name = name
        self.public_key = public_key
        self.private_key = private_key
        self.introduction_nanopub_uri = introduction_nanopub_uri


_load_profile = yatiml.load_function(Profile)


_dump_profile = yatiml.dump_function(Profile)


def get_orcid_id() -> str:
    """Returns the user's ORCID."""
    return get_profile().orcid_id


def get_public_key() -> str:
    """Returns the user's public key."""
    try:
        with open(get_profile().public_key, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise ProfileError(f'Public key file {get_profile().public_key} for nanopub not found.\n'
                           f'Maybe your nanopub profile was not set up yet or not set up '
                           f'correctly. \n{PROFILE_INSTRUCTIONS_MESSAGE}')


@lru_cache()
def get_profile() -> Profile:
    """Retrieve nanopub user profile.

    By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Returns:
        A Profile containing the data from the configuration file.

    Raises:
        yatiml.RecognitionError: If there is an error in the file.
    """
    try:
        return _load_profile(PROFILE_PATH)
    except (yatiml.RecognitionError, FileNotFoundError) as e:
        msg = (f'{e}\nYour nanopub profile has not been set up yet, or is not set up correctly.\n'
               f'{PROFILE_INSTRUCTIONS_MESSAGE}')
        raise ProfileError(msg)


def store_profile(profile: Profile) -> Path:
    """Stores the nanopub user profile.

    By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Args:
        profile: The profile to store as the user's profile.

    Returns:
        The path where the profile was stored.

    Raises:
        yatiml.RecognitionError: If there is an error in the file.
    """
    _dump_profile(profile, PROFILE_PATH)
    return PROFILE_PATH
