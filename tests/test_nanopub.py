from unittest import mock

import rdflib
from rdflib.namespace import RDF

from nanopub import namespaces, Nanopub

TEST_ASSERTION = (namespaces.AUTHOR.DrBob, namespaces.HYCL.claims, rdflib.Literal('This is a test'))
TEST_ORCID_ID = 'https://orcid.org/0000-0000-0000-0000'


def _get_mock_profile():
    mock_profile = mock.MagicMock()
    mock_profile.get_orcid_id.return_value = TEST_ORCID_ID

    return mock_profile


@mock.patch('nanopub.nanopub.profile', _get_mock_profile())
class TestNanopub:
    def test_nanopub_construction_with_bnode_introduced_concept(self):
        """
        Test Nanopub construction from assertion where a BNode is introduced as a concept.
        """
        test_uri = 'http://www.example.com/my-nanopub'
        test_concept_uri = 'http://www.example.com/my-nanopub#DrBob'  # This nanopub introduced DrBob
        assertion_rdf = rdflib.Graph()
        assertion_rdf.add((rdflib.term.BNode('DrBob'),
                           namespaces.HYCL.claims,
                           rdflib.Literal('This is a test')))

        nanopub = Nanopub.from_assertion(
            assertion_rdf=assertion_rdf,
            uri=rdflib.term.URIRef(test_uri),
            introduces_concept=rdflib.term.BNode('DrBob'),
            derived_from=rdflib.term.URIRef('http://www.example.com/another-nanopub'),
            attributed_to=TEST_ORCID_ID
        )
        assert str(nanopub.introduces_concept) == test_concept_uri

    def test_nanopub_from_assertion(self):
        """
        Test that Nanopub.from_assertion is creating an rdf graph with the right features (contexts)
        for a nanopub.
        """
        assertion_rdf = rdflib.Graph()
        assertion_rdf.add((namespaces.AUTHOR.DrBob, namespaces.HYCL.claims,
                           rdflib.Literal('This is a test')))

        nanopub = Nanopub.from_assertion(assertion_rdf)

        assert nanopub.rdf is not None
        assert (None, RDF.type, namespaces.NP.Nanopublication) in nanopub.rdf
        assert (None, namespaces.NP.hasAssertion, None) in nanopub.rdf
        assert (None, namespaces.NP.hasProvenance, None) in nanopub.rdf
        assert (None, namespaces.NP.hasPublicationInfo, None) in nanopub.rdf

        new_concept = rdflib.term.URIRef('www.purl.org/new/concept/test')
        nanopub = Nanopub.from_assertion(assertion_rdf, introduces_concept=new_concept)

        assert nanopub.rdf is not None
        assert (None, RDF.type, namespaces.NP.Nanopublication) in nanopub.rdf
        assert (None, namespaces.NP.hasAssertion, None) in nanopub.rdf
        assert (None, namespaces.NP.hasProvenance, None) in nanopub.rdf
        assert (None, namespaces.NP.hasPublicationInfo, None) in nanopub.rdf

        assert (None, namespaces.NPX.introduces, new_concept) in nanopub.rdf

    def test_nanopub_from_assertion_use_profile(self):
        assertion = rdflib.Graph()
        assertion.add(TEST_ASSERTION)

        result = Nanopub.from_assertion(assertion_rdf=assertion)

        assert (None, None, rdflib.URIRef(TEST_ORCID_ID)) in result.rdf
