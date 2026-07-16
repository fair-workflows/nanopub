import re
from urllib.parse import urlparse

ORCID_ID_REGEX = r'^https://orcid.org/(\d{4}-){3}\d{3}[\dXx]$'
ORCID_DOMAIN = "orcid.org"
ORCID_URL_PREFIX = f'https://{ORCID_DOMAIN}/'
_ORCID_ID_PATTERN = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dXx]$")


class OrcidID:
    def __init__(self, orcid_id: str):
        if not orcid_id:
            raise ValueError('The ORCID is not valid, please provide a valid ORCID.')

        raw = orcid_id.strip()

        is_bare = _ORCID_ID_PATTERN.fullmatch(raw) is not None

        parsed = urlparse(raw)
        is_url = False
        path_digits = None
        if parsed.scheme and parsed.hostname:
            if parsed.hostname == ORCID_DOMAIN:
                # path should be the hyphenated form
                candidate = parsed.path.lstrip("/")
                if _ORCID_ID_PATTERN.fullmatch(candidate):
                    is_url = True
                    path_digits = candidate

        if not (is_bare or is_url):
            raise ValueError(f'The ORCID {orcid_id} is not valid, please provide a valid ORCID.')

        # At this point, either raw is bare hyphenated, or path_digits contains it
        hyphenated = path_digits if path_digits is not None else raw

        digits = hyphenated.replace("-", "")
        if len(digits) != 16:
            raise ValueError(f'The ORCID {orcid_id} is not valid, please provide a valid ORCID.')

        # 0000-0000-0000-0000 is not a valid orcid_id, but it is accepted for test purposes and backwards compatibility
        # the check digit is not computed only for this case
        if digits != "0" * 16:
            base = digits[:-1]
            check_digit = digits[-1].upper()
            if not generate_check_digit(base) == check_digit:
                raise ValueError(f'The ORCID {orcid_id} is not valid, please provide a valid ORCID.')

        canonical_digits = digits.upper()
        hyphenated = f"{canonical_digits[0:4]}-{canonical_digits[4:8]}-{canonical_digits[8:12]}-{canonical_digits[12:16]}"
        self.orcid_id = f"{ORCID_URL_PREFIX}{hyphenated}"

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


def looks_like_orcid(agent_id: str) -> bool:
    """
    Return True if `agent_id` is either a bare hyphenated ORCID or an orcid.org URL.

    This performs a case-insensitive host check by parsing the URL with
    urllib.parse.urlparse and inspecting parsed.hostname (which is normalized to lowercase).
    """
    if not agent_id or not isinstance(agent_id, str):
        return False
    s = agent_id.strip()

    if _ORCID_ID_PATTERN.fullmatch(s):
        return True

    # try as URL: parse and check hostname and path
    parsed = urlparse(s)
    if parsed.scheme and parsed.hostname:
        # urlparse.lowercases hostname, so this is case-insensitive
        if parsed.hostname == ORCID_DOMAIN:
            return True
    return False
