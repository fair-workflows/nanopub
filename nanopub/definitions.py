from pathlib import Path

from rdflib import Namespace

ROOT_FILEPATH = Path(__file__).parent.parent
TESTS_FILEPATH = ROOT_FILEPATH / "tests"
TEST_RESOURCES_FILEPATH = TESTS_FILEPATH / "resources"
USER_CONFIG_DIR = Path.home() / ".nanopub"
DEFAULT_PROFILE_PATH = USER_CONFIG_DIR / "profile.yml"

BLAZEGRAPH_SERVER = 'http://localhost:9999/blazegraph/namespace/kb/sparql'

NANOPUB_TEST_SERVER = 'https://np.test.knowledgepixels.com/'
# List of servers: https://monitor.petapico.org/.csv
NANOPUB_SERVER_LIST = [
    'https://np.petapico.org/',
    'http://app.tkuhn.eculture.labs.vu.nl/nanopub-server-1/',
    'http://app.tkuhn.eculture.labs.vu.nl/nanopub-server-2/',
    'http://app.tkuhn.eculture.labs.vu.nl/nanopub-server-3/',
    'http://app.tkuhn.eculture.labs.vu.nl/nanopub-server-4/',
    'http://server.nanopubs.lod.labs.vu.nl/',
    'http://server.np.dumontierlab.com/',
]
NANOPUB_FETCH_FORMAT = "trig"

DUMMY_NANOPUB_URI = "http://purl.org/nanopub/temp/np"
DUMMY_NAMESPACE = Namespace(DUMMY_NANOPUB_URI + "#")
DUMMY_URI = DUMMY_NAMESPACE[""]

NP_TEMP_PREFIX = "http://purl.org/nanopub/temp/"
NP_PURL = "http://purl.org/np/"

MAX_NP_PER_INDEX = 1100
MAX_TRIPLES_PER_NANOPUB = 1200

RSA_KEY_SIZE = 2048

NANOPUB_GRLC_URLS = [
    "http://grlc.nanopubs.lod.labs.vu.nl/api/local/local/",
    "http://130.60.24.146:7881/api/local/local/",
    "https://openphacts.cs.man.ac.uk/nanopub/grlc/api/local/local/",
    "http://grlc.np.dumontierlab.com/api/local/local/"
    # These servers do currently not support
    # find_valid_signed_nanopubs_with_pattern (2020-12-21)
    # "https://grlc.nanopubs.knows.idlab.ugent.be/api/local/local/",
    # "http://grlc.np.scify.org/api/local/local/",
]
NANOPUB_TEST_GRLC_URL = "https://grlc.test.nps.knowledgepixels.com/api/local/local/"
