from unittest import mock

import pytest
import rdflib

from nanopub import namespaces, Publication, replace_in_rdf
from nanopub.definitions import DUMMY_NANOPUB_URI

TEST_ORCID_ID = 'https://orcid.org/0000-0000-0000-0000'


class TestPublication:
    test_rdf = rdflib.Graph()
    test_triple = (namespaces.AUTHOR.DrBob, rdflib.RDF.type, rdflib.FOAF.Person)
    test_rdf.add(test_triple)

    def test_from_assertion_introduced_concept_not_bnode(self):
        with pytest.raises(ValueError):
            Publication.from_assertion(self.test_rdf, introduces_concept='not a blank node')

    def test_from_assertion_with_bnode_introduced_concept(self):
        """
        Test Publication construction from assertion where a BNode is introduced as a concept.
        """
        publication = Publication.from_assertion(assertion_rdf=self.test_rdf,
                                                 introduces_concept=rdflib.term.BNode('DrBob'),
                                                 )
        test_concept_uri = DUMMY_NANOPUB_URI + '#DrBob'  # This nanopub introduced DrBob
        assert str(publication.introduces_concept) == test_concept_uri
        assert (None, namespaces.NPX.introduces, rdflib.URIRef(test_concept_uri)) in publication.rdf

    def test_construction_with_derived_from_as_list(self):
        """
        Test Publication construction from assertion where derived_from is a list.
        """
        derived_from_list = [   'http://www.example.com/another-nanopub', # This nanopub is derived from several sources
                                'http://www.example.com/and-another-nanopub',
                                'http://www.example.com/and-one-more' ]

        publication = Publication.from_assertion(assertion_rdf=self.test_rdf,
                                                 derived_from=derived_from_list)

        for uri in derived_from_list:
            assert (None, namespaces.PROV.wasDerivedFrom, rdflib.URIRef(uri)) in publication.rdf

    @mock.patch('nanopub.publication.profile')
    def test_from_assertion(self, mock_profile):
        """
        Test that Publication.from_assertion is creating an rdf graph with the right features (
        contexts) for a publication.
        """
        mock_profile.get_orcid_id.return_value = TEST_ORCID_ID
        publication = Publication.from_assertion(self.test_rdf)

        assert publication.rdf is not None
        assert (None, rdflib.RDF.type, namespaces.NP.Nanopublication) in publication.rdf
        assert (None, namespaces.NP.hasAssertion, None) in publication.rdf
        assert (None, namespaces.NP.hasProvenance, None) in publication.rdf
        assert (None, namespaces.NP.hasPublicationInfo, None) in publication.rdf
        assert (None, None, rdflib.URIRef(TEST_ORCID_ID)) in publication.rdf

    def test_from_assertion_provide_provenance_rdf(self):
        publication = Publication.from_assertion(assertion_rdf=self.test_rdf,
                                                 provenance_rdf=self.test_rdf)
        assert self.test_triple in publication.provenance

    def test_from_assertion_provide_pubinfo_rdf(self):
        publication = Publication.from_assertion(assertion_rdf=self.test_rdf,
                                                 pubinfo_rdf=self.test_rdf)
        assert self.test_triple in publication.pubinfo

    def test_from_assertion_double_derived_from_predicate(self):
        triple = (rdflib.term.BNode(''), namespaces.PROV.wasDerivedFrom, rdflib.URIRef('example'))
        provenance_rdf = rdflib.Graph()
        provenance_rdf.add(triple)
        with pytest.raises(ValueError):
            Publication.from_assertion(assertion_rdf=self.test_rdf,
                                       provenance_rdf=provenance_rdf,
                                       derived_from=rdflib.URIRef('example'))
        Publication.from_assertion(assertion_rdf=self.test_rdf)

    def test_from_assertion_double_attributed_to_predicate(self):
        triple = (rdflib.term.BNode(''), namespaces.PROV.wasAttributedTo, rdflib.URIRef('example'))
        provenance_rdf = rdflib.Graph()
        provenance_rdf.add(triple)
        with pytest.raises(ValueError):
            Publication.from_assertion(assertion_rdf=self.test_rdf,
                                       provenance_rdf=provenance_rdf,
                                       assertion_attributed_to=rdflib.URIRef('example'))
        with pytest.raises(ValueError):
            Publication.from_assertion(assertion_rdf=self.test_rdf,
                                       provenance_rdf=provenance_rdf,
                                       attribute_assertion_to_profile=True)
        Publication.from_assertion(assertion_rdf=self.test_rdf)

    def test_from_assertion_double_introduces_predicate(self):
        triple = (rdflib.term.BNode(''), namespaces.NPX.introduces, rdflib.URIRef('example'))
        pubinfo_rdf = rdflib.Graph()
        pubinfo_rdf.add(triple)
        with pytest.raises(ValueError):
            Publication.from_assertion(assertion_rdf=self.test_rdf,
                                       pubinfo_rdf=pubinfo_rdf,
                                       introduces_concept=rdflib.URIRef('example'))
        Publication.from_assertion(assertion_rdf=self.test_rdf)


def test_replace_in_rdf():
    g = rdflib.Graph()
    g.add((rdflib.Literal('DrBob'), rdflib.RDF.type, rdflib.Literal('Doctor')))
    g.add((rdflib.Literal('Alice'), rdflib.FOAF.knows, rdflib.Literal('DrBob')))
    replace_in_rdf(g, rdflib.Literal('DrBob'), rdflib.Literal('Alfonso'))
    assert (rdflib.Literal('Alfonso'), rdflib.RDF.type, rdflib.Literal('Doctor')) in g
    assert (rdflib.Literal('Alice'), rdflib.FOAF.knows, rdflib.Literal('Alfonso')) in g
    assert (rdflib.Literal('DrBob'), rdflib.RDF.type, rdflib.Literal('Doctor')) not in g
    assert (rdflib.Literal('Alice'), rdflib.FOAF.knows, rdflib.Literal('DrBob')) not in g
