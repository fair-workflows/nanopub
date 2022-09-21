from dataclasses import dataclass, asdict

@dataclass
class NanopubConfig:
    """Represents the configuration for nanopubs."""

    add_prov_generated_time: bool = True
    add_pubinfo_generated_time: bool = True

    attribute_assertion_to_profile: bool = False
    attribute_publication_to_profile: bool = True

    assertion_attributed_to: str = None
    publication_attributed_to: str = None

    derived_from: str = None


    dict = asdict
