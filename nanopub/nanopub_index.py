# -*- coding: utf-8 -*-
"""This module includes a client for the nanopub server.
"""

import os
import random
import tempfile
import warnings
from typing import List, Tuple, Union

import rdflib
import requests
from rdflib.namespace import DC, DCTERMS, RDF, RDFS, XSD

from nanopub import namespaces
from nanopub.definitions import DUMMY_NANOPUB_URI
from nanopub.java_wrapper import JavaWrapper
from nanopub.profile import Profile, get_profile
from nanopub.publication import Publication
from nanopub.nanopublication import Nanopublication

DUMMY_NAMESPACE = rdflib.Namespace(DUMMY_NANOPUB_URI + "#")
NP_URI = DUMMY_NAMESPACE[""]


class NanopubIndex(Nanopublication):
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
        add_pubinfo_generated_time=True,
        add_prov_generated_time=False,
        attribute_publication_to_profile=True,
    ) -> None:
        super().__init__(
            nanopub_profile=profile,
            add_pubinfo_generated_time=add_pubinfo_generated_time,
            add_prov_generated_time=add_prov_generated_time,
            attribute_publication_to_profile=attribute_publication_to_profile,
        )

        # assertion = rdflib.Graph()
        # assertion.bind("pav", namespaces.PAV)
        # assertion.bind("prov", namespaces.PROV)
        # assertion.bind("pmid", namespaces.PMID)
        # assertion.bind("orcid", namespaces.ORCID)
        # assertion.bind("ntemplate", namespaces.NTEMPLATE)

        for np in np_list:
            self.assertion.add((NP_URI, namespaces.NPX.includesElement, rdflib.URIRef(np)))

        self.pubinfo.add((NP_URI, RDF.type, namespaces.NPX.NanopubIndex))
        self.pubinfo.add((NP_URI, DC.title, rdflib.Literal(title)))
        self.pubinfo.add((NP_URI, DC.description, rdflib.Literal(description)))
        if see_also:
            self.pubinfo.add((NP_URI, RDFS.seeAlso, rdflib.URIRef(see_also)))
        for creator in creators:
            self.pubinfo.add((NP_URI, namespaces.PAV.createdBy, rdflib.URIRef(creator)))
        # TODO: use current time if not provided
        # datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
        self.pubinfo.add(
            (
                NP_URI,
                DCTERMS.created,
                rdflib.Literal(creation_time, datatype=XSD.dateTime, normalize=False),
            )
        )

        self.prov.add((DUMMY_NAMESPACE.assertion, RDF.type, namespaces.NPX.IndexAssertion))

        # publication = Publication.from_assertion(
        #     assertion_rdf=assertion,
        #     pubinfo_rdf=pubinfo,
        #     provenance_rdf=prov,
        #     nanopub_profile=profile,
        #     add_pubinfo_generated_time=True,
        #     add_prov_generated_time=False,
        #     attribute_publication_to_profile=True,
        # )
        # return publication
