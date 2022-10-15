from typing import Optional

from rdflib import Literal, URIRef
from rdflib.namespace import FOAF

from nanopub.config import NanopubConfig
from nanopub.namespaces import NPX
from nanopub.nanopub import Nanopub


class NanopubIntroduction(Nanopub):
    """Publish a Nanopub introduction to introduce a key pair for an ORCID

    Args:
        config: config for the nanopub
        host: the service where the keypair are hosted
    """

    def __init__(
        self,
        config: NanopubConfig,
        host: Optional[str] = None,
        # public_key: str = None,
    ) -> None:
        config.add_prov_generated_time = False
        config.add_pubinfo_generated_time = True
        config.attribute_publication_to_profile = True
        config.attribute_assertion_to_profile = True
        super().__init__(
            config=config,
        )

        # if not self.config.profile.public_key:
        #     log.info("Generating private/public pair keys")
        #     public_key = generate_keys(USER_CONFIG_DIR)

        key_declaration = self._dummy_namespace.keyDeclaration
        orcid_node = URIRef(self.config.profile.orcid_id)

        self.assertion.add((key_declaration, NPX.declaredBy, orcid_node))
        self.assertion.add((key_declaration, NPX.hasAlgorithm, Literal("RSA")))
        self.assertion.add((key_declaration, NPX.hasPublicKey, Literal(self.config.profile.public_key)))
        self.assertion.add((orcid_node, FOAF.name, Literal(self.config.profile.name)))
        if host:
            self.assertion.add((key_declaration, NPX.hasKeyLocation, URIRef(host)))
