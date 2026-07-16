import re

ORCID_ID_REGEX = r'^https://orcid.org/(\d{4}-){3}\d{3}(\d|X)$'
ORCID_URL_PREFIX = "https://orcid.org/"
_ORCID_ID_PATTERN = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]")


class OrcidID:
    def __init__(self, orcid_id: str):
        if _ORCID_ID_PATTERN.fullmatch(orcid_id):
            self.orcid_id = f"{ORCID_URL_PREFIX}{orcid_id}"
        elif re.match(ORCID_ID_REGEX, orcid_id):
            self.orcid_id = orcid_id
        else:
            raise ValueError(f'The ORCID {orcid_id} is not valid, please provide a valid ORCID.')
        digits = orcid_id.removeprefix(ORCID_URL_PREFIX).replace("-", "")
        # 0000-0000-0000-0000 is not a valid orcid_id, but it is accepted for test purposes and backwards compatibility
        # the check digit is not computed only for this case
        if digits != "0" * 16:
            base = digits[:-1]
            check_digit = digits[-1].upper()
            if not generate_check_digit(base) == check_digit:
                raise ValueError(f'The ORCID {orcid_id} is not valid, please provide a valid ORCID.')

    def __str__(self):
        return self.orcid_id


def generate_check_digit(base_digits: str) -> str:
    """Generates check digit as per ISO 7064 11,2."""
    total = 0
    for char in base_digits:
        total = (total + int(char)) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    return "X" if result == 10 else str(result)
