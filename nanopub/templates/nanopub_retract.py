from rdflib import URIRef

from nanopub.namespaces import NPX
from nanopub.nanopub import Nanopub
from nanopub.nanopub_conf import NanopubConf
from nanopub.profile import ProfileError


class NanopubRetract(Nanopub):
    """Retract a nanopublication.

    Publish a retraction nanpublication that declares retraction of the nanopublication that
    corresponds to the 'uri' argument.

    Args:
        conf: config for the nanopub
        uri (str): The uri pointing to the to-be-retracted nanopublication
        force (bool): Toggle using force to retract, this will even retract the
            nanopublication if it is signed with a different public key than the one
            in the user profile.
    """

    def __init__(
        self,
        conf: NanopubConf,
        uri: str,
        force: bool = False,
    ) -> None:
        conf.add_prov_generated_time = True
        conf.add_pubinfo_generated_time = True
        conf.attribute_publication_to_profile = True
        conf.attribute_assertion_to_profile = True
        super().__init__(
            conf=conf,
        )
        if not self.profile:
            raise ProfileError("No profile provided, cannot generate a Nanopub to retract another nanopub")

        if not force:
            self._check_public_keys_match(uri)
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
        np = Nanopub(uri)
        their_public_key = np.metadata.public_key
        print("KEYS")
        print(their_public_key)
        print(self.conf.profile.public_key)
        if their_public_key != self.conf.profile.public_key:
            print("python cant compare 2 strings")
        if (
            their_public_key is not None
            and their_public_key != self.conf.profile.public_key
        ):
            raise AssertionError(
                "The public key in your profile does not match the public key"
                "that the publication that you want to retract is signed "
                "with. Use force=True to force retraction anyway."
            )
