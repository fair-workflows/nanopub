from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class NanopubConfig:
    """Represents the configuration for nanopubs."""

    add_prov_generated_time: bool = True
    add_pubinfo_generated_time: bool = True

    attribute_assertion_to_profile: bool = False
    attribute_publication_to_profile: bool = True

    assertion_attributed_to: Optional[str] = None
    publication_attributed_to: Optional[str] = None

    derived_from: Optional[str] = None


    dict = asdict
