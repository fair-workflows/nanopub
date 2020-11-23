from unittest import mock

import pytest
import rdflib
from rdflib.namespace import RDF

from nanopub import namespaces, Publication
from nanopub.definitions import DUMMY_NANOPUB_URI

TEST_ORCID_ID = 'https://orcid.org/0000-0000-0000-0000'


class TestPublication:
    test_assertion = rdflib.Graph()
    test_assertion.add((namespaces.AUTHOR.DrBob,
                        namespaces.HYCL.claims,
                        rdflib.Literal('This is a test')))

    def test_from_assertion_introduced_concept_not_blank_node(self):
        with pytest.raises(ValueError):
            Publication.from_assertion(self.test_assertion, introduces_concept='not a blank node')

    def test_construction_with_bnode_introduced_concept(self):
        """
        Test Publication construction from assertion where a BNode is introduced as a concept.
        """


        publication = Publication.from_assertion(
            assertion_rdf=self.test_assertion,
            introduces_concept=rdflib.term.BNode('DrBob'),
            derived_from=rdflib.term.URIRef('http://www.example.com/another-nanopub'),
            attributed_to=TEST_ORCID_ID
        )
        test_concept_uri = DUMMY_NANOPUB_URI + '#DrBob'  # This nanopub introduced DrBob
        assert str(publication.introduces_concept) == test_concept_uri

    def test_construction_with_derived_from_as_list(self):
        """
        Test Publication construction from assertion where derived_from is a list.
        """
        derived_from_list = [   'http://www.example.com/another-nanopub', # This nanopub is derived from several sources
                                'http://www.example.com/and-another-nanopub',
                                'http://www.example.com/and-one-more' ]

        publication = Publication.from_assertion(
            assertion_rdf=self.test_assertion,
            derived_from=derived_from_list,
            attributed_to=TEST_ORCID_ID
        )

        for uri in derived_from_list:
            assert (None, namespaces.PROV.wasDerivedFrom, rdflib.URIRef(uri)) in publication.rdf

    @mock.patch('nanopub.publication.profile')
    def test_from_assertion(self, mock_profile):
        """
        Test that Publication.from_assertion is creating an rdf graph with the right features (
        contexts) for a publication.
        """
        mock_profile.get_orcid_id.return_value = TEST_ORCID_ID
        nanopub = Publication.from_assertion(self.test_assertion)

        assert nanopub.rdf is not None
        assert (None, RDF.type, namespaces.NP.Nanopublication) in nanopub.rdf
        assert (None, namespaces.NP.hasAssertion, None) in nanopub.rdf
        assert (None, namespaces.NP.hasProvenance, None) in nanopub.rdf
        assert (None, namespaces.NP.hasPublicationInfo, None) in nanopub.rdf

        new_concept = rdflib.term.URIRef('www.purl.org/new/concept/test')
        nanopub = Publication.from_assertion(self.test_assertion, introduces_concept=new_concept)

        assert nanopub.rdf is not None
        assert (None, RDF.type, namespaces.NP.Nanopublication) in nanopub.rdf
        assert (None, namespaces.NP.hasAssertion, None) in nanopub.rdf
        assert (None, namespaces.NP.hasProvenance, None) in nanopub.rdf
        assert (None, namespaces.NP.hasPublicationInfo, None) in nanopub.rdf

        assert (None, namespaces.NPX.introduces, new_concept) in nanopub.rdf

        assert (None, None, rdflib.URIRef(TEST_ORCID_ID)) in nanopub.rdf
