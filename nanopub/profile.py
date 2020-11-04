from pathlib import Path

from nanopub.definitions import PROFILE_PATH
import yaml

_profile = None


def get_orcid():
    return get_profile()['orcid']


def get_profile():
    """
    Retrieve nanopub user profile
    :return:
    """

    global _profile
    if not _profile:
        _profile = _load_profile()
    return _profile


def _load_profile():
    path = PROFILE_PATH
    with path.open('r') as f:
        return yaml.load(f)
