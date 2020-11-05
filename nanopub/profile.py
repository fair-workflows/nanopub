from functools import lru_cache
from typing import Dict

import yaml

from nanopub.definitions import PROFILE_PATH

_profile = None


def get_orcid_id():
    return get_profile()['orcid']


@lru_cache()
def get_profile() -> Dict[str, any]:
    """
    Retrieve nanopub user profile. By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Returns: A dict with all settings stored in the user profile yaml file.

    """
    path = PROFILE_PATH
    with path.open('r') as f:
        return yaml.load(f)
