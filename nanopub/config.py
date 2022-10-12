from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class NanopubConfig:
    """Represents the configuration for nanopubs.

    Args:
        add_prov_generated_time: add generated time to provenance
        add_pubinfo_generated_time: add generated time to pubinfo
        attribute_assertion_to_profile: bool
        attribute_publication_to_profile: bool
        assertion_attributed_to: Optional str
        publication_attributed_to: Optional str
        derived_from: Optional str
    """

    add_prov_generated_time: bool = False
    add_pubinfo_generated_time: bool = False

    attribute_assertion_to_profile: bool = False
    attribute_publication_to_profile: bool = False

    assertion_attributed_to: Optional[str] = None
    publication_attributed_to: Optional[str] = None

    derived_from: Optional[str] = None


    dict = asdict
