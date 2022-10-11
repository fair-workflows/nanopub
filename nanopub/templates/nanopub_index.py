# -*- coding: utf-8 -*-
"""This module includes a client for the nanopub server.
"""

from typing import List

from rdflib import Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, RDFS, XSD

from nanopub.definitions import DUMMY_NAMESPACE, DUMMY_URI
from nanopub.namespaces import NPX, PAV
from nanopub.nanopub import Nanopub
from nanopub.nanopub_config import NanopubConfig
from nanopub.profile import Profile


class NanopubIndex(Nanopub):
    """
    Publish a list of nanopub URIs in a Nanopub Index

    Args:
        np_list: List of nanopub URIs
        title: Title of the Nanopub Index
        description: Description of the Nanopub Index
        creation_time: Creation time of the Nanopub Index, in format YYYY-MM-DDThh-mm-ss
        creators: List of the ORCID of the creators of the Nanopub Index
        see_also: A URL to a page with further information on the Nanopub Index
    """

    def __init__(
        self,
        np_list: List[str],
        title: str,
        description: str,
        creation_time: str,
        creators: List[str],
        see_also: str = None,
        profile: Profile = None,
        config: NanopubConfig = NanopubConfig(
            add_prov_generated_time=False,
            add_pubinfo_generated_time=True,
            attribute_publication_to_profile=True,
        ),
        top_level: bool = False,
    ) -> None:
        super().__init__(
            profile=profile,
            config=config,
        )

        for np in np_list:
            if top_level:
                self.assertion.add((DUMMY_URI, NPX.appendsIndex, URIRef(np)))
            else:
                self.assertion.add((DUMMY_URI, NPX.includesElement, URIRef(np)))

        self.pubinfo.add((DUMMY_URI, RDF.type, NPX.NanopubIndex))
        self.pubinfo.add((DUMMY_URI, DC.title, Literal(title)))
        self.pubinfo.add((DUMMY_URI, DC.description, Literal(description)))
        if see_also:
            self.pubinfo.add((DUMMY_URI, RDFS.seeAlso, URIRef(see_also)))
        for creator in creators:
            self.pubinfo.add((DUMMY_URI, PAV.createdBy, URIRef(creator)))
        # TODO: use current time if not provided
        # datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() ?
        self.pubinfo.add(
            (
                DUMMY_URI,
                DCTERMS.created,
                Literal(creation_time, datatype=XSD.dateTime, normalize=False),
            )
        )

        self.provenance.add((DUMMY_NAMESPACE.assertion, RDF.type, NPX.IndexAssertion))
