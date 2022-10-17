"""This module includes a client for the nanopub server.
"""

from rdflib import RDF, RDFS, Literal, URIRef

from nanopub.namespaces import HYCL
from nanopub.nanopub import Nanopub
from nanopub.nanopub_conf import NanopubConf
from nanopub.profile import ProfileError


class NanopubClaim(Nanopub):
    """Quickly claim a statement.

    Constructs statement triples around the provided text following the Hypotheses and Claims
    Ontology (http://purl.org/petapico/o/hycl).

    Args:
        conf: config for the nanopub
        claim (str): the text of the statement, example: 'All cats are grey'
    """

    def __init__(
        self,
        claim: str,
        conf: NanopubConf,
    ) -> None:
        conf.add_prov_generated_time = True
        conf.add_pubinfo_generated_time = True
        conf.attribute_publication_to_profile = True
        super().__init__(
            conf=conf,
        )
        if not self.profile:
            raise ProfileError("No profile provided, cannot generate a Nanopub Claim")

        this_statement = self._namespace["claim"]
        # this_statement = BNode("mystatement")
        self.assertion.add((this_statement, RDF.type, HYCL.Statement))
        self.assertion.add((this_statement, RDFS.label, Literal(claim)))

        orcid_id_uri = URIRef(self.profile.orcid_id)
        self.provenance.add((orcid_id_uri, HYCL.claims, this_statement))
