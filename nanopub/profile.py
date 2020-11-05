from functools import lru_cache

import yaml

from nanopub.definitions import PROFILE_PATH

_profile = None


def get_orcid_id():
    return get_profile()['orcid']


@lru_cache()
def get_profile():
    """
    Retrieve nanopub user profile
    :return:
    """
    path = PROFILE_PATH
    with path.open('r') as f:
        return yaml.load(f)
