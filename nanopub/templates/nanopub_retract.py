"""This module includes a client for the nanopub server.
"""

from rdflib import URIRef

from nanopub.config import NanopubConfig
from nanopub.namespaces import NPX
from nanopub.nanopub import Nanopub
from nanopub.profile import Profile


class NanopubRetract(Nanopub):
    """Retract a nanopublication.

    Publish a retraction nanpublication that declares retraction of the nanopublication that
    corresponds to the 'uri' argument.

    Args:
        uri (str): The uri pointing to the to-be-retracted nanopublication
        force (bool): Toggle using force to retract, this will even retract the
            nanopublication if it is signed with a different public key than the one
            in the user profile.
    """

    def __init__(
        self,
        uri: str,
        profile: Profile,
        force: bool = False,
        config: NanopubConfig = NanopubConfig(
            add_prov_generated_time=True,
            add_pubinfo_generated_time=True,
            attribute_publication_to_profile=True,
            attribute_assertion_to_profile=True,
        ),
    ) -> None:
        super().__init__(
            profile=profile,
            config=config,
        )

        # if not force:
        #     self._check_public_keys_match(uri)
        orcid_id = self.profile.orcid_id
        self.assertion.add(
            (URIRef(orcid_id), NPX.retracts, URIRef(uri))
        )


    def _check_public_keys_match(self, uri):
        """Check for matching public keys of a nanopublication with the profile.

        Raises:
            AssertionError: When the nanopublication is signed with a public key that does not
                match the public key in the profile
        """
        publication = self.fetch(uri)
        their_public_key = publication.signed_with_public_key
        print("KEYS")
        print(their_public_key)
        print(self.profile.get_public_key())
        if their_public_key != self.profile.get_public_key():
            print("python cant compare 2 strings")
        if (
            their_public_key is not None
            and their_public_key != self.profile.get_public_key()
        ):
            raise AssertionError(
                "The public key in your profile does not match the public key"
                "that the publication that you want to retract is signed "
                "with. Use force=True to force retraction anyway."
            )
