"""This module includes a client for the nanopub server.
"""

from rdflib import RDF, RDFS, BNode, Literal, URIRef

from nanopub.config import NanopubConfig
from nanopub.namespaces import HYCL
from nanopub.nanopub import Nanopub


class NanopubClaim(Nanopub):
    """Quickly claim a statement.

    Constructs statement triples around the provided text following the Hypotheses and Claims
    Ontology (http://purl.org/petapico/o/hycl).

    Args:
        claim (str): the text of the statement, example: 'All cats are grey'
    """

    def __init__(
        self,
        claim: str,
        config: NanopubConfig,
    ) -> None:
        config.add_prov_generated_time = True
        config.add_pubinfo_generated_time = True
        config.attribute_publication_to_profile = True
        super().__init__(
            config=config,
        )

        this_statement = BNode("mystatement")
        self.assertion.add((this_statement, RDF.type, HYCL.Statement))
        self.assertion.add((this_statement, RDFS.label, Literal(claim)))

        orcid_id_uri = URIRef(self.profile.orcid_id)
        self.provenance.add((orcid_id_uri, HYCL.claims, this_statement))
