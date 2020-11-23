from unittest import mock

import pytest

from nanopub import profile


@mock.patch('nanopub.profile.get_profile', return_value={'orcid_id': ''})
def test_no_orcid_id(mock_get_profile):
    with pytest.raises(profile.ProfileError):
        profile.get_orcid_id()
