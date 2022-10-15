"""
This module holds code for representing the RDF of nanopublications, as well as helper functions to
make handling RDF easier.
"""
import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import rdflib
from rdflib import BNode, ConjunctiveGraph, Graph, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, FOAF, PROV, RDF, XSD

from nanopub.config import NanopubConfig
from nanopub.definitions import (
    DUMMY_NAMESPACE,
    DUMMY_NANOPUB_URI,
    MAX_TRIPLES_PER_NANOPUB,
    NANOPUB_TEST_SERVER,
    MalformedNanopubError,
    log,
)
from nanopub.namespaces import HYCL, NP, NPX, NTEMPLATE, ORCID, PAV
from nanopub.profile import ProfileError
from nanopub.signer import add_signature, publish_graph, verify_signature, verify_trusty


class Nanopub:
    """A Nanopub object, containing: the RDF that defines the nanopublication;
    configuration for formatting and publishing the nanopub; functions for validating, signing, publishing

    Attributes:
        rdf (rdflib.ConjunctiveGraph): The full RDF graph of this nanopublication
        assertion (rdflib.Graph): The part of the graph describing the assertion.
        pubinfo (rdflib.Graph): The part of the graph describing the publication information.
        provenance (rdflib.Graph): The part of the graph describing the provenance.
        source_uri (str): The URI of the nanopublication that this Publication represents (if applicable)
        introduces_concept (rdflib.BNode): The concept that is introduced by this Publication.
        signed_with_public_key: The public key that this Publication is signed with.
        config (NanopubConfig): Config for the nanopub
    """

    def __init__(
        self,
        # *args,
        assertion: Graph = Graph(),
        provenance: Graph = Graph(),
        pubinfo: Graph = Graph(),
        rdf: Union[ConjunctiveGraph, Path] = None,
        source_uri: str = None,
        introduces_concept: BNode = None,
        config: NanopubConfig = NanopubConfig(),
        # **kwargs
    ) -> None:
        # print(config.profile)
        self._profile = config.profile
        self._source_uri = source_uri
        self._concept_uri = None
        self._config = config
        self._published = False
        self._dummy_namespace = DUMMY_NAMESPACE
        if self._config.use_test_server:
            self._config.use_server = NANOPUB_TEST_SERVER


        if isinstance(rdf, ConjunctiveGraph):
            np_uris = self.extract_np_uris(rdf)
            self._dummy_namespace = Namespace(np_uris['np_namespace'])
            self._rdf = self._preformat_graph(rdf)
        elif isinstance(rdf, Path):
            self._rdf = self._preformat_graph(ConjunctiveGraph())
            self._rdf.parse(rdf)
            np_uris = self.extract_np_uris(self._rdf)
            self._dummy_namespace = Namespace(np_uris['np_namespace'])
        else:
            self._rdf = self._preformat_graph(ConjunctiveGraph())

        # print(self._dummy_namespace)
        # print(self._rdf.serialize(format='trig'))

        self._head = Graph(self._rdf.store, self._dummy_namespace.Head)
        self._assertion = Graph(self._rdf.store, self._dummy_namespace.assertion)
        self._provenance = Graph(self._rdf.store, self._dummy_namespace.provenance)
        self._pubinfo = Graph(self._rdf.store, self._dummy_namespace.pubinfo)

        if not rdf:
            self._head.add((self._dummy_namespace[""], RDF.type, NP.Nanopublication))
            self._head.add(
                (self._dummy_namespace[""], NP.hasAssertion, self._dummy_namespace.assertion)
            )
            self._head.add(
                (
                    self._dummy_namespace[""],
                    NP.hasProvenance,
                    self._dummy_namespace.provenance,
                )
            )
            self._head.add(
                (
                    self._dummy_namespace[""],
                    NP.hasPublicationInfo,
                    self._dummy_namespace.pubinfo,
                )
            )

        self._assertion += assertion
        self._provenance += provenance
        self._pubinfo += pubinfo

        self._validate_nanopub_arguments(
            introduces_concept=introduces_concept,
            derived_from=self._config.derived_from,
            assertion_attributed_to=self._config.assertion_attributed_to,
            attribute_assertion_to_profile=self._config.attribute_assertion_to_profile,
            # publication_attributed_to=publication_attributed_to,
        )
        self._handle_generated_at_time(
            self._config.add_pubinfo_generated_time,
            self._config.add_prov_generated_time
        )
        assertion_attributed_to = self._config.assertion_attributed_to
        if self._config.attribute_assertion_to_profile:
            assertion_attributed_to = rdflib.URIRef(self.profile.orcid_id)
        self._handle_assertion_attributed_to(assertion_attributed_to)
        self._handle_publication_attributed_to(
            self._config.attribute_publication_to_profile,
            self._config.publication_attributed_to
        )
        self._handle_derived_from(derived_from=self._config.derived_from)

        # Concatenate prefixes declarations from all provided graphs in the main graph
        for user_rdf in [assertion, provenance, pubinfo]:
            if user_rdf is not None:
                for prefix, namespace in user_rdf.namespaces():
                    self._rdf.bind(prefix, namespace)


    def _preformat_graph(self, g: ConjunctiveGraph) -> ConjunctiveGraph:
        """Add a few default namespaces"""
        # Add default namespaces
        g.bind("", None, replace=True)
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
        # g = self._replace_blank_nodes(g)
        return g


    def update_from_signed(self, signed_g: ConjunctiveGraph) -> None:
        """Update the pub RDF to the signed one"""
        np_uris = self.extract_np_uris(signed_g)
        self._dummy_namespace = Namespace(np_uris['np_namespace'])
        self._source_uri = self.get_source_uri_from_graph
        self._rdf = signed_g
        self._head = Graph(self._rdf.store, self._dummy_namespace.Head)
        self._assertion = Graph(self._rdf.store, self._dummy_namespace.assertion)
        self._provenance = Graph(self._rdf.store, self._dummy_namespace.provenance)
        self._pubinfo = Graph(self._rdf.store, self._dummy_namespace.pubinfo)


    def sign(self) -> None:
        """Sign a Nanopub object."""
        if len(self.rdf) > MAX_TRIPLES_PER_NANOPUB:
            raise MalformedNanopubError(f"Nanopublication contains {len(self.rdf)} triples, which is more than the {MAX_TRIPLES_PER_NANOPUB} authorized")
        if not self._config.profile:
            raise ProfileError("Profile not available, cannot sign the nanopub")
        if self.source_uri:
            raise MalformedNanopubError("The nanopub have already been signed")

        if self.is_valid:
            # Sign the nanopub
            signed_g = add_signature(self.rdf, self._config.profile, self._dummy_namespace)
            self.update_from_signed(signed_g)
            log.info(f"Signed {self.source_uri}")


    def publish(self) -> None:
        """Publish a Nanopub object."""
        if not self.source_uri:
            self.sign()

        publish_graph(self.rdf, use_server=self._config.use_server)
        log.info(f'Published {self.source_uri} to {self._config.use_server}')
        self.published = True

        if self.introduces_concept:
            concept_uri = str(self.introduces_concept)
            # Replace the DUMMY_NANOPUB_URI with the actually published nanopub uri. This is
            # necessary if a blank node was passed as introduces_concept. In that case the
            # Nanopub.from_assertion method replaces the blank node with the base nanopub's URI
            # and appends a fragment, given by the 'name' of the blank node. For example, if a
            # blank node with name 'step' was passed as introduces_concept, the concept will be
            # published with a URI that looks like [published nanopub URI]#step.
            concept_uri = concept_uri.replace(
                DUMMY_NANOPUB_URI, self.source_uri
            )
            self.concept_uri = concept_uri
            log.info(f"Published concept to {concept_uri}")


    def extract_np_uris(self, g: ConjunctiveGraph) -> dict:
        """Extract a nanopub URI, namespace and head/assertion/prov/pubinfo contexts from a Graph"""
        get_np_query = """PREFIX np: <http://www.nanopub.org/nschema#>

SELECT DISTINCT ?np ?head ?assertion ?provenance ?pubinfo WHERE {
    GRAPH ?head {
        ?np a np:Nanopublication ;
            np:hasAssertion ?assertion ;
            np:hasProvenance ?provenance ;
            np:hasPublicationInfo ?pubinfo .
    }
    GRAPH ?assertion {
        ?assertionS ?assertionP ?assertionO .
    }
    GRAPH ?provenance {
        ?provenanceS ?provenanceP ?provenanceO .
    }
    GRAPH ?pubinfo {
        ?pubinfoS ?pubinfoP ?pubinfoO .
    }
}
"""
        qres = g.query(get_np_query)
        if len(qres) < 1:
            raise MalformedNanopubError(
                "\033[1mNo nanopublication\033[0m have been found in the provided RDF. "
                "It should contain a np:Nanopublication object in a Head graph, pointing to 3 graphs: assertion, provenance and pubinfo"
            )
        if len(qres) > 1:
            for row in qres:
                print(row)
            raise MalformedNanopubError(
                "\033[1mMultiple nanopublications\033[0m are defined in this graph. "
                "The Nanopub object can only handles 1 nanopublication at a time"
            )
        np_contexts: dict = {}
        for row in qres:
            np_contexts['head'] = row.head
            np_contexts['assertion'] = row.assertion
            np_contexts['provenance'] = row.provenance
            np_contexts['pubinfo'] = row.pubinfo

        np_uri = None
        np_namespace = None
        for c_label, c_uri in np_contexts.items():
            extract_uri = re.search(r'^(.*)(\/|#)(.*)$', str(c_uri), re.IGNORECASE)
            if extract_uri:
                base_uri = extract_uri.group(1)
                separator_char = extract_uri.group(2)

                if np_namespace and str(np_namespace) != str(base_uri + separator_char):
                    raise MalformedNanopubError(
                        f"\033[1mMultiple nanopublications URIs\033[0m are defined in this graph, e.g. {np_namespace} and {base_uri + separator_char}"
                        "The Nanopub object can only handles 1 nanopublication at a time"
                    )
                np_uri = base_uri
                np_namespace = base_uri + separator_char
        np_contexts['np_uri'] = np_uri
        np_contexts['np_namespace'] = np_namespace
        return np_contexts


    @property
    def has_valid_signature(self) -> bool:
        verify_trusty(self._rdf, self.source_uri, self._dummy_namespace)
        verify_signature(self._rdf, self.source_uri, self._dummy_namespace)
        return True


    @property
    def is_valid(self) -> bool:
        """Check if a nanopublication is valid"""
        np_contexts = self.extract_np_uris(self._rdf)
        np_uri = np_contexts['np_uri']

        graph_count = 0
        for c in self._rdf.contexts():
            if len(list(self._rdf.quads((None, None, None, c)))) > 0:
                graph_count += 1
        if graph_count != 4:
            raise MalformedNanopubError(f"Too many graphs found in the provided RDF: {graph_count}. A Nanopub should have only 4 graphs (Head, assertion, provenance, pubinfo)")

        # for c in self._rdf.contexts():
        # Check if any of the graph is empty
        if len(self._head) < 1:
            raise MalformedNanopubError("The Head graph is empty")
        if len(self._assertion) < 1:
            raise MalformedNanopubError("The assertion graph is empty")
        if len(self._provenance) < 1:
            raise MalformedNanopubError("The provenance graph is empty")
        if len(self._pubinfo) < 1:
            raise MalformedNanopubError("The pubinfo graph is empty")

        found_prov = False
        for s, p, o in self._provenance:
            if str(s) == str(np_contexts['assertion']):
                found_prov = True
                break
        if not found_prov:
            raise MalformedNanopubError(f"The provenance graph should contain at least one triple with the assertion graph URI as subject: \033[1m{np_contexts['assertion']}\033[0m")

        found_pubinfo = False
        for s, p, o in self._pubinfo:
            if str(s) == str(np_uri) or str(s) == str(np_contexts['np_namespace']):
                found_pubinfo = True
                break
        if not found_pubinfo:
            raise MalformedNanopubError(f"The pubinfo graph should contain at least one triple that has the nanopub URI as subject: \033[1m{np_uri}\033[0m")

        if len(self._head) != 4:
            raise MalformedNanopubError(f"Too many triples in the nanopublication Head graph: {len(self._head)} instead of 4")

        if self.source_uri:
            if self.has_valid_signature is False:
                raise MalformedNanopubError("The nanopub is not valid")
        return True


    @property
    def rdf(self) -> ConjunctiveGraph:
        return self._rdf

    @property
    def head(self):
        return self._head

    @property
    def assertion(self):
        return self._assertion

    @property
    def provenance(self):
        return self._provenance

    @property
    def pubinfo(self):
        return self._pubinfo


    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def source_uri(self):
        # return self._source_uri
        if self._source_uri:
            return self._source_uri
        else:
            return self.get_source_uri_from_graph

    @source_uri.setter
    def source_uri(self, value):
        self._source_uri = value

    @property
    def published(self):
        return self._published

    @published.setter
    def published(self, value):
        self._published = value

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
        for s, p, o in self._pubinfo.triples((None, NPX.introduces, None)):
            concepts_introduced.append(o)

        if len(concepts_introduced) == 0:
            return None
        elif len(concepts_introduced) == 1:
            return concepts_introduced[0]
        else:
            raise MalformedNanopubError("Nanopub introduces multiple concepts")


    @property
    def get_source_uri_from_graph(self) -> Optional[str]:
        """Get the source URI of the nanopublication from the header.

        This is usually something like:
        http://purl.org/np/RAnksi2yDP7jpe7F6BwWCpMOmzBEcUImkAKUeKEY_2Yus
        """
        for s in self._rdf.subjects(rdflib.RDF.type, NP.Nanopublication):
            extract_trusty = re.search(r'^[a-z0-9+.-]+:\/\/[a-zA-Z0-9\/._-]+\/(RA.*)$', str(s), re.IGNORECASE)
            if extract_trusty:
                # extract_trusty.group(1)
                return str(s)
        return None


    @property
    def signed_with_public_key(self) -> Optional[str]:
        if not self.get_source_uri_from_graph:
            return None
        public_keys = list(
            self._rdf.objects(URIRef(self.get_source_uri_from_graph + "#sig"), NPX.hasPublicKey)
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
            return True
        else:
            return False


    def __str__(self) -> str:
        s = ""
        if self.source_uri:
            s += f"Nanopub URI: \033[1m{self.source_uri}\033[0m\n"
        s += self._rdf.serialize(format="trig")
        return s


    def _handle_generated_at_time(
        self, add_pubinfo_generated_time: bool, add_prov_generated_time: bool
    ) -> None:
        """Handler for `Nanopub` constructor."""
        creationtime = rdflib.Literal(datetime.now(), datatype=XSD.dateTime)
        if add_pubinfo_generated_time:
            self._pubinfo.add(
                (self._dummy_namespace[""], PROV.generatedAtTime, creationtime)
            )
        if add_prov_generated_time:
            self._provenance.add(
                (
                    self._dummy_namespace.assertion,
                    PROV.generatedAtTime,
                    creationtime,
                )
            )


    def _handle_assertion_attributed_to(self, assertion_attributed_to: Optional[str]) -> None:
        """Handler for `Nanopub` constructor."""
        if assertion_attributed_to:
            assertion_attributed_to = URIRef(assertion_attributed_to)
            self._provenance.add(
                (
                    self._dummy_namespace.assertion,
                    PROV.wasAttributedTo,
                    assertion_attributed_to,
                )
            )


    def _handle_publication_attributed_to(
        self,
        attribute_publication_to_profile: bool,
        publication_attributed_to: Optional[str],
    ) -> None:
        """Handler for `Nanopub` constructor."""
        if attribute_publication_to_profile:
            if not self._profile:
                raise MalformedNanopubError("No nanopub profile provided, but attribute_publication_to_profile is enabled")
            if publication_attributed_to is None:
                publication_attributed_to = rdflib.URIRef(self._profile.orcid_id)
            else:
                publication_attributed_to = rdflib.URIRef(publication_attributed_to)
            self._pubinfo.add(
                (
                    self._dummy_namespace[""],
                    PROV.wasAttributedTo,
                    publication_attributed_to,
                )
            )


    def _handle_derived_from(self, derived_from: Optional[str]):
        """Handler for `Nanopub` constructor."""
        if derived_from:
            if isinstance(derived_from, list):
                list_of_uris = derived_from
            else:
                list_of_uris = [derived_from]

            for derived_from_uri in list_of_uris:
                derived_from_uri = rdflib.URIRef(derived_from_uri)
                self._provenance.add(
                    (
                        self._dummy_namespace.assertion,
                        PROV.wasDerivedFrom,
                        derived_from_uri,
                    )
                )

    def _handle_introduces_concept(self, introduces_concept: Union[BNode, URIRef]):
        """Handler for `Nanopub` constructor."""
        if introduces_concept:
            introduces_concept = self._dummy_namespace[str(introduces_concept)]
            self._pubinfo.add(
                (self._dummy_namespace[""], NPX.introduces, introduces_concept)
            )

    def _validate_nanopub_arguments(
        self,
        derived_from: Optional[str],
        assertion_attributed_to: Optional[str],
        attribute_assertion_to_profile: bool,
        introduces_concept: Optional[BNode],
        # publication_attributed_to,
    ) -> None:
        """
        Validate arguments method.
        """
        if assertion_attributed_to and attribute_assertion_to_profile:
            raise MalformedNanopubError(
                "If you pass a URI for the assertion_attributed_to argument, you cannot pass "
                "attribute_assertion_to_profile=True, because the assertion will already be "
                "attributed to the value passed in assertion_attributed_to argument. Set "
                "attribute_assertion_to_profile=False or do not pass the assertion_attributed_to "
                "argument."
            )

        if introduces_concept and not isinstance(introduces_concept, BNode):
            raise MalformedNanopubError(
                "If you want a nanopublication to introduce a concept, you need to "
                'pass it as an rdflib.term.BNode("concept_name"). This will make '
                "sure it is referred to from the nanopublication uri namespace upon "
                "publishing."
            )

        if self._provenance:
            if (
                derived_from
                and (None, PROV.wasDerivedFrom, None) in self._provenance
            ):
                raise MalformedNanopubError(
                    "The provenance_rdf that you passed already contains the "
                    "prov:wasDerivedFrom predicate, so you cannot also use the "
                    "derived_from argument"
                )
            if (
                assertion_attributed_to
                and (None, PROV.wasAttributedTo, None) in self._provenance
            ):
                raise MalformedNanopubError(
                    "The provenance_rdf that you passed already contains the "
                    "prov:wasAttributedTo predicate, so you cannot also use the "
                    "assertion_attributed_to argument"
                )
            if (
                attribute_assertion_to_profile
                and (None, PROV.wasAttributedTo, None) in self._provenance
            ):
                raise MalformedNanopubError(
                    "The provenance_rdf that you passed already contains the "
                    "prov:wasAttributedTo predicate, so you cannot also use the "
                    "attribute_assertion_to_profile argument"
                )
        # if self._pubinfo:
        #     if (
        #         introduces_concept
        #         and (None, NPX.introduces, None) in self._pubinfo
        #     ):
        #         raise MalformedNanopubError(
        #             "The pubinfo_rdf that you passed already contains the "
        #             "npx:introduces predicate, so you cannot also use the "
        #             "introduces_concept argument"
        #         )
        #     if (None, PROV.wasAttributedTo, None) in self._pubinfo:
        #         raise MalformedNanopubError(
        #             "The pubinfo_rdf that you passed should not contain the "
        #             "prov:wasAttributedTo predicate. If you wish to change "
        #             "who the publication is attributed to, please use the "
        #             "publication_attributed_to argument instead. By default "
        #             "this is the ORCID set in your profile, but you can set "
        #             "it to another URI if desired."
        #         )


    # def _replace_blank_nodes(self, rdf: ConjunctiveGraph) -> ConjunctiveGraph:
    #     """Replace blank nodes.

    #     Replace any blank nodes in the supplied RDF with a corresponding uri in the
    #     dummy_namespace.'Blank nodes' here refers specifically to rdflib.term.BNode objects. When
    #     publishing, the dummy_namespace is replaced with the URI of the actual nanopublication.

    #     For example, if the nanopub's URI is www.purl.org/ABC123 then the blank node will be
    #     replaced with a concrete URIRef of the form www.purl.org/ABC123#blanknodename where
    #     'blanknodename' is the name of the rdflib.term.BNode object.

    #     This is to solve the problem that a user may wish to use the nanopublication to introduce
    #     a new concept. This new concept needs its own URI (it cannot simply be given the
    #     nanopublication's URI), but it should still lie within the space of the nanopub.
    #     Furthermore, the URI the nanopub is published to is not known ahead of time.
    #     """
    #     for s, p, o in rdf:
    #         if isinstance(s, BNode):
    #             rdf.remove((s, p, o))
    #             s = self._dummy_namespace[str(s)]
    #             rdf.add((s, p, o))
    #         if isinstance(o, BNode):
    #             rdf.remove((s, p, o))
    #             o = self._dummy_namespace[str(o)]
    #             rdf.add((s, p, o))
    #     return rdf


# TODO: remove?
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
