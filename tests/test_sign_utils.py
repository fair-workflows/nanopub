import re
from copy import deepcopy

from rdflib import Dataset, URIRef, Literal, Namespace, Graph
from rdflib.namespace import FOAF

from nanopub import Nanopub
from nanopub.definitions import DUMMY_NAMESPACE, NP_PREFIX, NP_TEMP_PREFIX
from nanopub.namespaces import NPX
from nanopub.profile import Profile
from nanopub.sign_utils import add_signature
from nanopub.trustyuri.rdf import RdfUtils
from tests.conftest import default_conf, profile_test


class TestVerifyTrusty:

    def test_real_uri_returns_true(self):
        np = Nanopub(source_uri="https://w3id.org/np/RAAwn-ONPeKgxxWJNBDtVotYfZcFyppCy_z8ASy2mJLKY")
        assert np.has_valid_trusty

    def test_get_quads_preserves_named_graph_context_identifier(self):
        ds = Dataset()
        graph_uri = URIRef("https://example.org/g")
        ds.add((URIRef("https://example.org/s"), URIRef("https://example.org/p"), Literal("x"), graph_uri))

        quads = RdfUtils.get_quads(ds)
        assert len(quads) == 1
        assert quads[0][0] == graph_uri  # context should not collapse to None


class TestAddSignature:

    def test_add_signature(self):
        input_g = Dataset()
        dummy_namespace = Namespace(NP_TEMP_PREFIX)
        pubinfo_uri = URIRef(f"{dummy_namespace}pubinfo")
        pubinfo_g = Graph(store=input_g.store, identifier=pubinfo_uri)

        output_g = add_signature(input_g, profile_test, dummy_namespace, pubinfo_g)

        # Find the generated signature subject
        sig_subjects = [s for s, _, _, _ in output_g.quads((None, NPX.hasSignature, None, None))]
        assert len(sig_subjects) == 1
        sig_subject = sig_subjects[0]

        # Use hasAlgorithm to pin the graph context used for signature metadata
        matches = list(output_g.quads((sig_subject, NPX.hasAlgorithm, Literal("RSA"), None)))
        assert len(matches) == 1
        _, _, _, found_graph = matches[0]
        assert found_graph is not None
        ctx_graph = output_g.graph(found_graph)
        assert (sig_subject, NPX.hasPublicKey, Literal(profile_test.public_key)) in ctx_graph
        assert (sig_subject, NPX.signedBy, URIRef(profile_test.agent_id))

        sig_values = [o for _, _, o, _ in output_g.quads((sig_subject, NPX.hasSignature, None, None))]
        assert len(sig_values) == 1
        assert isinstance(sig_values[0], Literal)
        assert str(sig_values[0]).strip() != ""

        # Signature target must be the nanopub URI (same namespace, no fragment)
        targets = [o for _, _, o, _ in output_g.quads((sig_subject, NPX.hasSignatureTarget, None, None))]
        assert len(targets) == 1
        target_uri = str(targets[0])
        assert target_uri.startswith(NP_PREFIX)
        artifact_code = target_uri.removeprefix(NP_PREFIX)
        assert re.fullmatch(r"RA[A-Za-z0-9\-_]{43}", artifact_code)

        # Ensure temp namespace was replaced everywhere in URIRefs
        for s, p, o, c in output_g.quads((None, None, None, None)):
            for term in (s, p, o, c):
                if isinstance(term, URIRef):
                    assert not str(term).startswith(NP_TEMP_PREFIX)


class TestSelfSignedIntroduction:
    """A signer that is a sub-IRI of the nanopub it signs (self-signed agent introduction).

    An agent's IRI should be a sub-IRI of its own introduction, so that the
    introduction can be self-signed with the agent's key in a single step. The
    signer IRI must therefore go through the same temp-URI replacement as every
    other term, both when hashing (so it is normalized as a self-reference) and
    when emitting the final trusty URIs. See nanopub-java issue #127.
    """

    @staticmethod
    def _self_signing_profile(agent_id: str) -> Profile:
        profile = deepcopy(profile_test)
        profile.agent_id = agent_id
        profile.name = "My Bot"
        return profile

    def test_temp_signer_iri_is_replaced_by_trusty_sub_iri(self):
        agent_id = str(DUMMY_NAMESPACE["my-bot"])
        conf = deepcopy(default_conf)
        conf.profile = self._self_signing_profile(agent_id)

        np = Nanopub(conf=conf)
        key_declaration = np.namespace["keyDeclaration"]
        bot = URIRef(agent_id)
        np.assertion.add((key_declaration, NPX.declaredBy, bot))
        np.assertion.add((key_declaration, NPX.hasAlgorithm, Literal("RSA")))
        np.assertion.add((key_declaration, NPX.hasPublicKey, Literal(conf.profile.public_key)))
        np.assertion.add((bot, FOAF.name, Literal(conf.profile.name)))

        np.sign()

        signed_by = [o for _, _, o, _ in np.rdf.quads((None, NPX.signedBy, None, None))]
        assert len(signed_by) == 1
        # The signer keeps its temp URI in nanopub-java before the fix for #127
        assert not str(signed_by[0]).startswith(NP_TEMP_PREFIX)
        assert str(signed_by[0]) == f"{np.source_uri}/my-bot"

        # The self-reference must be part of the hash, so both must still check out
        assert np.has_valid_signature
        assert np.has_valid_trusty

    def test_external_signer_iri_is_left_untouched(self):
        conf = deepcopy(default_conf)
        conf.profile = self._self_signing_profile("https://orcid.org/0000-0002-1825-0097")

        np = Nanopub(conf=conf)
        np.assertion.add((
            URIRef("https://example.org/s"),
            URIRef("https://example.org/p"),
            Literal("o"),
        ))
        np.sign()

        signed_by = [o for _, _, o, _ in np.rdf.quads((None, NPX.signedBy, None, None))]
        assert len(signed_by) == 1
        assert str(signed_by[0]) == "https://orcid.org/0000-0002-1825-0097"
        assert np.has_valid_signature
        assert np.has_valid_trusty
