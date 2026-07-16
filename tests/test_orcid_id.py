import pytest

from nanopub.orcid_id import OrcidID, generate_check_digit, ORCID_URL_PREFIX


class TestOrcidID:
    def test_valid_bare_orcid_is_expanded(self):
        # Known valid ORCID (example from ORCID docs)
        bare = "0000-0002-1825-0097"
        o = OrcidID(bare)
        assert str(o) == f"{ORCID_URL_PREFIX}{bare}"

    def test_valid_orcid_url_is_preserved(self):
        url = "https://orcid.org/0000-0002-1825-0097"
        o = OrcidID(url)
        assert str(o) == url

    def test_invalid_format_raises_value_error(self):
        with pytest.raises(ValueError):
            OrcidID("not-an-orcid")

    def test_invalid_check_digit_raises_value_error(self):
        # Same as a valid ORCID but with wrong last digit
        wrong = "0000-0002-1825-0098"
        with pytest.raises(ValueError):
            OrcidID(wrong)

    def test_generate_check_digit_all_zeros(self):
        # For base digits all zeros (15 zeros), the check digit should be "1"
        base = "0" * 15
        assert generate_check_digit(base) == "1"
        # The full ORCID would be 0000-0000-0000-0001
        full_orcid = "0000-0000-0000-0001"
        o = OrcidID(full_orcid)
        assert str(o) == f"{ORCID_URL_PREFIX}{full_orcid}"

    def test_generate_check_digit_known_example(self):
        # Using the known valid ORCID "0000-0002-1825-0097"
        full = "0000-0002-1825-0097"
        digits = full.replace("-", "")
        base = digits[:-1]
        expected_check = digits[-1]
        assert generate_check_digit(base) == expected_check

    def test_orcid_id_all_zeros(self):
        # For test purposes and backwards compatibility, this is the only non-valid  orcid_id that is accepted
        full_orcid = "0000-0000-0000-0000"
        o = OrcidID(full_orcid)
        assert str(o) == f"{ORCID_URL_PREFIX}{full_orcid}"
