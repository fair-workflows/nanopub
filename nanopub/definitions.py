from pathlib import Path

ROOT_FILEPATH = Path(__file__).parent.parent
PKG_FILEPATH = Path(__file__).parent
TESTS_FILEPATH = ROOT_FILEPATH / 'tests'
TEST_RESOURCES_FILEPATH = TESTS_FILEPATH / 'resources'
USER_CONFIG_DIR = Path.home() / '.nanopub'
PROFILE_PATH = USER_CONFIG_DIR / 'profile.yml'

# Dummy URI when referring to a nanopub, will be replaced with published URI when publishing.
DUMMY_NANOPUB_URI = 'http://purl.org/nanopub/temp/mynanopub'
