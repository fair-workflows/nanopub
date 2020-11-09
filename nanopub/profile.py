from functools import lru_cache
from pathlib import Path
from typing import Dict

import yaml

from nanopub.definitions import PROFILE_PATH

ORCID_ID = 'orcid_id'
NAME = 'name'
PUBLIC_KEY = 'public_key'
PRIVATE_KEY = 'private_key'


def get_orcid_id():
    return get_profile()['orcid_id']


@lru_cache()
def get_profile() -> Dict[str, any]:
    """
    Retrieve nanopub user profile. By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Returns: A dict with all settings stored in the user profile yaml file.

    """
    path = PROFILE_PATH
    with path.open('r') as f:
        return yaml.load(f)


def store_profile(name: str, orcid: str, public_key: Path, private_key: Path, profile_nanopub_uri: str = None):
    profile = {NAME: name, ORCID_ID: orcid, PUBLIC_KEY: str(public_key), PRIVATE_KEY: str(private_key)}

    if profile_nanopub_uri:
        profile['profile_nanopub'] = profile_nanopub_uri

    with PROFILE_PATH.open('w') as f:
        yaml.dump(profile, f)

    return PROFILE_PATH
