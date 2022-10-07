import logging
from pathlib import Path

from rdflib import Namespace, URIRef

ROOT_FILEPATH = Path(__file__).parent.parent
TESTS_FILEPATH = ROOT_FILEPATH / "tests"
TEST_RESOURCES_FILEPATH = TESTS_FILEPATH / "resources"
USER_CONFIG_DIR = Path.home() / ".nanopub"
PROFILE_PATH = USER_CONFIG_DIR / "profile.yml"

# Dummy URI when referring to a nanopub, will be replaced with published URI when publishing.
# DUMMY_NANOPUB_URI = "http://purl.org/np/ARTIFACTCODE-PLACEHOLDER"
# DUMMY_NAMESPACE = Namespace(DUMMY_NANOPUB_URI + "/")
# DUMMY_URI = URIRef(DUMMY_NANOPUB_URI)

DUMMY_NANOPUB_URI = "http://purl.org/nanopub/temp/mynanopub"
DUMMY_NAMESPACE = Namespace(DUMMY_NANOPUB_URI + "#")
DUMMY_URI = DUMMY_NAMESPACE[""]

FINAL_NANOPUB_URI = "http://purl.org/np/"

MAX_NP_PER_INDEX = 1100
MAX_TRIPLES_PER_NANOPUB = 1200

log = logging.getLogger()
