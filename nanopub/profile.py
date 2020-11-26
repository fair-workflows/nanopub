from functools import lru_cache
from pathlib import Path
from typing import Optional

import yatiml

from nanopub.definitions import PROFILE_PATH


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
        nanopub_uri: URI of the user's profile nanopub
    """
    def __init__(
            self,
            orcid_id: str, name: str,
            public_key: Path, private_key: Path,
            nanopub_uri: Optional[str] = None
            ) -> None:
        """Create a Profile."""
        self.orcid_id = orcid_id
        self.name = name
        self.public_key = public_key
        self.private_key = private_key
        self.nanopub_uri = nanopub_uri

    @classmethod
    def _yatiml_savorize(cls, node: yatiml.Node) -> None:
        node.rename_attribute('profile_nanopub', 'nanopub_uri')

    @classmethod
    def _yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.remove_attributes_with_default_values(cls)
        node.rename_attribute('nanopub_uri', 'profile_nanopub')


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
        raise ProfileError('Your profile was not setup yet or not setup correctly. To setup '
                           'your profile see instructions in Readme.md')


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
    except yatiml.RecognitionError as e:
        msg = (f'{e}\nYour profile has not been set up yet, or is not set up correctly. To set'
               f' up your profile, see the instructions in README.md.')
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
