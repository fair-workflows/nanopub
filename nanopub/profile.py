from functools import lru_cache
from pathlib import Path
from typing import Dict

import yaml

from nanopub.definitions import PROFILE_PATH

ORCID_ID = 'orcid_id'
NAME = 'name'
PUBLIC_KEY_FILEPATH = 'public_key'
PRIVATE_KEY_FILEPATH = 'private_key'
PROFILE_NANOPUB = 'profile_nanopub'


class ProfileError(RuntimeError):
    """
    Error to be raised if profile is not setup correctly.
    """
    pass


def get_orcid_id():
    orcid_id = get_profile()[ORCID_ID]
    if not orcid_id:
        raise ProfileError('Your profile was not setup yet or not setup correctly. To setup '
                           'your profile see instructions in Readme.md')
    return orcid_id


def get_public_key():
    filepath = get_profile()[PUBLIC_KEY_FILEPATH]
    with open(filepath, 'r') as f:
        return f.read()


@lru_cache()
def get_profile() -> Dict[str, any]:
    """
    Retrieve nanopub user profile. By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Returns: A dict with all settings stored in the user profile yaml file.

    """
    path = PROFILE_PATH
    with path.open('r') as f:
        return yaml.load(f)


def store_profile(name: str, orcid_id: str, public_key: Path, private_key: Path,
                  profile_nanopub_uri: str = None):
    profile = {NAME: name, ORCID_ID: orcid_id, PUBLIC_KEY_FILEPATH: str(public_key),
               PRIVATE_KEY_FILEPATH: str(private_key)}

    if profile_nanopub_uri:
        profile[PROFILE_NANOPUB] = profile_nanopub_uri

    with PROFILE_PATH.open('w') as f:
        yaml.dump(profile, f)

    return PROFILE_PATH
