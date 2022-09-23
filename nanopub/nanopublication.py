# -*- coding: utf-8 -*-
"""
This module holds code for representing the RDF of nanopublications, as well as helper functions to
make handling RDF easier.
"""
import warnings
from copy import deepcopy
from datetime import datetime
from urllib.parse import urldefrag

import rdflib
from rdflib import Graph, Literal, Namespace, URIRef, ConjunctiveGraph, BNode
from rdflib.namespace import DC, DCTERMS, PROV, RDF, RDFS, VOID, XSD, FOAF

from nanopub import namespaces, profile
from nanopub.definitions import DUMMY_NAMESPACE
from nanopub.profile import Profile
from nanopub.namespaces import HYCL, NP, NPX, PAV, ORCID, NTEMPLATE
from nanopub.nanopub_config import NanopubConfig


class Nanopublication:
    """
    Representation of the rdf that comprises a nanopublication

    Attributes:
        rdf (rdflib.ConjunctiveGraph): The full RDF graph of this nanopublication
        assertion (rdflib.Graph): The part of the graph describing the assertion.
        pubinfo (rdflib.Graph): The part of the graph describing the publication information.
        provenance (rdflib.Graph): The part of the graph describing the provenance.
        source_uri (str): The URI of the nanopublication that this Publication represents (if
            applicable)
        introduces_concept: The concept that is introduced by this Publication.
        signed_with_public_key: The public key that this Publication is signed with.
        is_test_publication: Whether this is a test publication
    """

    def __init__(
        self,
        # *args,
        assertion: Graph = Graph(),
        provenance: Graph = Graph(),
        pubinfo: Graph = Graph(),
        rdf: ConjunctiveGraph = None,
        source_uri: str = None,
        introduces_concept: BNode = None,
        config: NanopubConfig = NanopubConfig(),
        profile: Profile = None
        # **kwargs
    ) -> None:
        self._profile = profile
        self._source_uri = source_uri
        self._concept_uri = None
        self._signed_file = None
        self.config = config

        if rdf:
            self._rdf = self._preformat_graph(rdf)
        else:
            self._rdf = self._preformat_graph(ConjunctiveGraph())

        self.head = Graph(self._rdf.store, DUMMY_NAMESPACE.Head)
        self.assertion = Graph(self._rdf.store, DUMMY_NAMESPACE.assertion)
        self.provenance = Graph(self._rdf.store, DUMMY_NAMESPACE.provenance)
        self.pubinfo = Graph(self._rdf.store, DUMMY_NAMESPACE.pubInfo)

        self.head.add((DUMMY_NAMESPACE[""], RDF.type, NP.Nanopublication))
        self.head.add(
            (DUMMY_NAMESPACE[""], NP.hasAssertion, DUMMY_NAMESPACE.assertion)
        )
        self.head.add(
            (
                DUMMY_NAMESPACE[""],
                NP.hasProvenance,
                DUMMY_NAMESPACE.provenance,
            )
        )
        self.head.add(
            (
                DUMMY_NAMESPACE[""],
                NP.hasPublicationInfo,
                DUMMY_NAMESPACE.pubInfo,
            )
        )

        self.assertion += assertion
        self.provenance += provenance
        self.pubinfo += pubinfo

        self._validate_from_assertion_arguments(
            introduces_concept=introduces_concept,
            derived_from=self.config.derived_from,
            assertion_attributed_to=self.config.assertion_attributed_to,
            attribute_assertion_to_profile=self.config.attribute_assertion_to_profile,
            # publication_attributed_to=publication_attributed_to,
        )
        self._handle_generated_at_time(
            self.config.add_pubinfo_generated_time,
            self.config.add_prov_generated_time
        )
        assertion_attributed_to = self.config.assertion_attributed_to
        if self.config.attribute_assertion_to_profile:
            assertion_attributed_to = rdflib.URIRef(self.profile.orcid_id)
        self._handle_assertion_attributed_to(assertion_attributed_to)
        self._handle_publication_attributed_to(
            self.config.attribute_publication_to_profile,
            self.config.publication_attributed_to
        )
        self._handle_derived_from(derived_from=self.config.derived_from)

        # Concatenate prefixes declarations from all provided graphs in the main graph
        for user_rdf in [assertion, provenance, pubinfo]:
            if user_rdf is not None:
                for prefix, namespace in user_rdf.namespaces():
                    self._rdf.bind(prefix, namespace)
                # cls._replace_blank_nodes(rdf=user_rdf)

        # Extract the Head, pubinfo, provenance and assertion graphs from the assigned nanopub rdf
        # self._graphs = {}
        # for c in rdf.contexts():
        #     graphid = urldefrag(c.identifier).fragment.lower()
        #     self._graphs[graphid] = c
        # Check all four expected graphs are provided
        # expected_graphs = ["head", "pubinfo", "provenance", "assertion"]
        # for expected in expected_graphs:
        #     if expected not in self._graphs.keys():
        #         raise ValueError(
        #             f"Expected to find {expected} graph in nanopub rdf, "
        #             f"but not found. Graphs found: {list(self._graphs.keys())}."
        #         )

    def _preformat_graph(self, g: Graph) -> Graph:
        """Replace blank nodes and add a few default namespaces

        Replace any blank nodes in the supplied RDF with a corresponding uri in the
        dummy_namespace.'Blank nodes' here refers specifically to rdflib.term.BNode objects. When
        publishing, the dummy_namespace is replaced with the URI of the actual nanopublication.

        For example, if the nanopub's URI is www.purl.org/ABC123 then the blank node will be
        replaced with a concrete URIRef of the form www.purl.org/ABC123#blanknodename where
        'blanknodename' is the name of the rdflib.term.BNode object.

        This is to solve the problem that a user may wish to use the nanopublication to introduce
        a new concept. This new concept needs its own URI (it cannot simply be given the
        nanopublication's URI), but it should still lie within the space of the nanopub.
        Furthermore, the URI the nanopub is published to is not known ahead of time.
        """
        # Add default namespaces
        g.bind("", DUMMY_NAMESPACE)
        g.bind("np", NP)
        g.bind("npx", NPX)
        g.bind("prov", PROV)
        g.bind("pav", PAV)
        g.bind("hycl", HYCL)
        g.bind("dc", DC)
        g.bind("dcterms", DCTERMS)
        g.bind("orcid", ORCID)
        g.bind("ntemplate", NTEMPLATE)
        g.bind("foaf", FOAF)

        self._replace_blank_nodes(g)
        return g


    def _replace_blank_nodes(self, rdf):
        """Replace blank nodes.

        Replace any blank nodes in the supplied RDF with a corresponding uri in the
        dummy_namespace.'Blank nodes' here refers specifically to rdflib.term.BNode objects. When
        publishing, the dummy_namespace is replaced with the URI of the actual nanopublication.

        For example, if the nanopub's URI is www.purl.org/ABC123 then the blank node will be
        replaced with a concrete URIRef of the form www.purl.org/ABC123#blanknodename where
        'blanknodename' is the name of the rdflib.term.BNode object.

        This is to solve the problem that a user may wish to use the nanopublication to introduce
        a new concept. This new concept needs its own URI (it cannot simply be given the
        nanopublication's URI), but it should still lie within the space of the nanopub.
        Furthermore, the URI the nanopub is published to is not known ahead of time.
        """
        for s, p, o in rdf:
            rdf.remove((s, p, o))
            if isinstance(s, BNode):
                s = DUMMY_NAMESPACE[str(s)]
            if isinstance(o, BNode):
                o = DUMMY_NAMESPACE[str(o)]
            rdf.add((s, p, o))


    def _validate_from_assertion_arguments(
        self,
        introduces_concept: BNode,
        derived_from,
        assertion_attributed_to,
        attribute_assertion_to_profile: bool,
        # publication_attributed_to,
    ):
        """
        Validate arguments for `from_assertion` method.
        """
        if assertion_attributed_to and attribute_assertion_to_profile:
            raise ValueError(
                "If you pass a URI for the assertion_attributed_to argument, you cannot pass "
                "attribute_assertion_to_profile=True, because the assertion will already be "
                "attributed to the value passed in assertion_attributed_to argument. Set "
                "attribute_assertion_to_profile=False or do not pass the assertion_attributed_to "
                "argument."
            )

        if introduces_concept and not isinstance(introduces_concept, BNode):
            raise ValueError(
                "If you want a nanopublication to introduce a concept, you need to "
                'pass it as an rdflib.term.BNode("concept_name"). This will make '
                "sure it is referred to from the nanopublication uri namespace upon "
                "publishing."
            )

        if self.provenance:
            if (
                derived_from
                and (None, PROV.wasDerivedFrom, None) in self.provenance
            ):
                raise ValueError(
                    "The provenance_rdf that you passed already contains the "
                    "prov:wasDerivedFrom predicate, so you cannot also use the "
                    "derived_from argument"
                )
            if (
                assertion_attributed_to
                and (None, PROV.wasAttributedTo, None) in self.provenance
            ):
                raise ValueError(
                    "The provenance_rdf that you passed already contains the "
                    "prov:wasAttributedTo predicate, so you cannot also use the "
                    "assertion_attributed_to argument"
                )
            if (
                attribute_assertion_to_profile
                and (None, PROV.wasAttributedTo, None) in self.provenance
            ):
                raise ValueError(
                    "The provenance_rdf that you passed already contains the "
                    "prov:wasAttributedTo predicate, so you cannot also use the "
                    "attribute_assertion_to_profile argument"
                )
        if self.pubinfo:
            if (
                introduces_concept
                and (None, NPX.introduces, None) in self.pubinfo
            ):
                raise ValueError(
                    "The pubinfo_rdf that you passed already contains the "
                    "npx:introduces predicate, so you cannot also use the "
                    "introduces_concept argument"
                )
            if (None, PROV.wasAttributedTo, None) in self.pubinfo:
                raise ValueError(
                    "The pubinfo_rdf that you passed should not contain the "
                    "prov:wasAttributedTo predicate. If you wish to change "
                    "who the publication is attributed to, please use the "
                    "publication_attributed_to argument instead. By default "
                    "this is the ORCID set in your profile, but you can set "
                    "it to another URI if desired."
                )



    def _handle_generated_at_time(
        self, add_pubinfo_generated_time, add_prov_generated_time
    ):
        """Handler for `from_assertion` method."""
        creationtime = rdflib.Literal(datetime.now(), datatype=XSD.dateTime)
        if add_pubinfo_generated_time:
            self.pubinfo.add(
                (DUMMY_NAMESPACE[""], PROV.generatedAtTime, creationtime)
            )
        if add_prov_generated_time:
            self.provenance.add(
                (
                    DUMMY_NAMESPACE.assertion,
                    PROV.generatedAtTime,
                    creationtime,
                )
            )


    def _handle_assertion_attributed_to(self, assertion_attributed_to):
        """Handler for `from_assertion` method."""
        if assertion_attributed_to:
            assertion_attributed_to = URIRef(assertion_attributed_to)
            self.provenance.add(
                (
                    DUMMY_NAMESPACE.assertion,
                    PROV.wasAttributedTo,
                    assertion_attributed_to,
                )
            )


    def _handle_publication_attributed_to(
        self,
        attribute_publication_to_profile,
        publication_attributed_to,
    ):
        """Handler for `from_assertion` method."""
        if attribute_publication_to_profile:
            if not self._profile:
                raise ValueError("No nanopub profile provided, but attribute_publication_to_profile is enabled")
            if publication_attributed_to is None:
                publication_attributed_to = rdflib.URIRef(self._profile.orcid_id)
            else:
                publication_attributed_to = rdflib.URIRef(publication_attributed_to)
            self.pubinfo.add(
                (
                    DUMMY_NAMESPACE[""],
                    PROV.wasAttributedTo,
                    publication_attributed_to,
                )
            )


    def _handle_derived_from(self, derived_from):
        """Handler for `from_assertion` method."""
        if derived_from:
            if isinstance(derived_from, list):
                list_of_uris = derived_from
            else:
                list_of_uris = [derived_from]

            for derived_from_uri in list_of_uris:
                derived_from_uri = rdflib.URIRef(derived_from_uri)
                self.provenance.add(
                    (
                        DUMMY_NAMESPACE.assertion,
                        PROV.wasDerivedFrom,
                        derived_from_uri,
                    )
                )


    def _handle_introduces_concept(self, introduces_concept):
        """Handler for `from_assertion` method."""
        if introduces_concept:
            introduces_concept = DUMMY_NAMESPACE[str(introduces_concept)]
            self.pubinfo.add(
                (DUMMY_NAMESPACE[""], NPX.introduces, introduces_concept)
            )

    @property
    def rdf(self):
        return self._rdf

    # @property
    # def assertion(self):
    #     return self._assertion

    # @property
    # def pubinfo(self):
    #     return self._pubinfo

    # @property
    # def provenance(self):
    #     return self._provenance

    @property
    def source_uri(self):
        return self._source_uri

    @source_uri.setter
    def source_uri(self, value):
        self._source_uri = value

    @property
    def signed_file(self):
        return self._signed_file

    @signed_file.setter
    def signed_file(self, value):
        self._signed_file = value

    @property
    def concept_uri(self):
        return self._concept_uri

    @concept_uri.setter
    def concept_uri(self, value):
        self._concept_uri = value

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value

    @property
    def introduces_concept(self):
        concepts_introduced = list()
        for s, p, o in self.pubinfo.triples((None, NPX.introduces, None)):
            concepts_introduced.append(o)

        if len(concepts_introduced) == 0:
            return None
        elif len(concepts_introduced) == 1:
            return concepts_introduced[0]
        else:
            raise ValueError("Nanopub introduces multiple concepts")

    @property
    def _self_ref(self):
        """Get the self reference (i.e. 'this') from the header.

        This is usually something like:
        http://purl.org/np/RAnksi2yDP7jpe7F6BwWCpMOmzBEcUImkAKUeKEY_2Yus
        """
        return list(
            self.head.subjects(
                predicate=rdflib.RDF.type, object=NP.Nanopublication
            )
        )[0]

    @property
    def signed_with_public_key(self):
        if not self._source_uri:
            return None
        public_keys = list(
            self.pubinfo.objects(self._self_ref + "#sig", NPX.hasPublicKey)
        )
        if len(public_keys) > 0:
            public_key = str(public_keys[0])
            if len(public_keys) > 1:
                warnings.warn(
                    f"Nanopublication is signed with multiple public keys, we will use "
                    f"this one: {public_key}"
                )
            return public_key
        else:
            return None

    @property
    def is_test_publication(self) -> bool:
        if self._source_uri is None:
            return None
        else:
            return "test" in self._source_uri


    def __str__(self):
        s = f"Original source URI = {self._source_uri}\n"
        s += self._rdf.serialize(format="trig")
        return s

    # @property
    # def signed_file_rdf(self) -> ConjunctiveGraph:
    #     if not self.signed_file:
    #         raise ValueError("No signed file available for this Nanopublication")
    #     g = ConjunctiveGraph()
    #     g.parse(self.signed_file, format="trig")
    #     return g


def replace_in_rdf(rdf: Graph, oldvalue, newvalue):
    """Replace values in RDF.

    Replace all subjects or objects matching `oldvalue` with `newvalue`. Replaces in place.

    Args:
        rdf (rdflib.Graph): The RDF graph in which we want to replace nodes
        oldvalue: The value to be replaced
        newvalue: The value to replace with
    """
    for s, p, o in rdf:
        if s == oldvalue:
            rdf.remove((s, p, o))
            rdf.add((newvalue, p, o))
        elif o == oldvalue:
            rdf.remove((s, p, o))
            rdf.add((s, p, newvalue))
