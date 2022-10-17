from dataclasses import asdict, dataclass
from typing import Optional

from rdflib import Namespace, URIRef

from nanopub.definitions import NANOPUB_SERVER_LIST
from nanopub.profile import Profile


@dataclass
class NanopubConf:
    """Represents the configuration for nanopubs.

    Args:
        profile: Profile of the user publishing the nanopub
        use_test_server: A boolean to automatically use the test server
        use_server: The URL of the server that will be used to publish the nanopub
        add_prov_generated_time: add generated time to provenance
        add_pubinfo_generated_time: add generated time to pubinfo
        attribute_assertion_to_profile: bool
        attribute_publication_to_profile: bool
        assertion_attributed_to: Optional str
        publication_attributed_to: Optional str
        derived_from: Optional str
    """

    profile: Optional[Profile] = None

    use_test_server: bool = False
    use_server: str = NANOPUB_SERVER_LIST[0]

    add_prov_generated_time: bool = False
    add_pubinfo_generated_time: bool = False

    attribute_assertion_to_profile: bool = False
    attribute_publication_to_profile: bool = False

    assertion_attributed_to: Optional[str] = None
    publication_attributed_to: Optional[str] = None

    derived_from: Optional[str] = None


    dict = asdict


# TODO: fix definition of all nanopub URIs
# test the comparison in retract
@dataclass
class NanopubUris:
    """Represents the URIs and namespace used in a nanopub.

    Args:
        namespace: Namespace used in the nanopub
        np_uri: the URI of the nanopub
    """

    namespace: Namespace
    np_uri: URIRef
    head: URIRef
    assertion: URIRef
    provenance: URIRef
    pubinfo: URIRef
    signature: URIRef

    dict = asdict
