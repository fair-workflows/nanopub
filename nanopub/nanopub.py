"""
This module holds code for representing the RDF of nanopublications, as well as helper functions to
make handling RDF easier.
"""
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import rdflib
import requests
from rdflib import BNode, ConjunctiveGraph, Graph, URIRef
from rdflib.namespace import DC, DCTERMS, FOAF, PROV, RDF, XSD

from nanopub.definitions import DUMMY_NANOPUB_URI, MAX_TRIPLES_PER_NANOPUB, NANOPUB_FETCH_FORMAT, NANOPUB_TEST_SERVER
from nanopub.namespaces import HYCL, NP, NPX, NTEMPLATE, ORCID, PAV
from nanopub.nanopub_conf import NanopubConf
from nanopub.profile import ProfileError
from nanopub.sign_utils import add_signature, publish_graph, verify_signature, verify_trusty
from nanopub.utils import MalformedNanopubError, NanopubMetadata, extract_np_metadata, log


class Nanopub:
    """A Nanopub object, containing: the RDF that defines the nanopublication;
    configuration for formatting and publishing the nanopub; functions for validating, signing, publishing

    Attributes:
        config (NanopubConfig): Config for the nanopub
        rdf (rdflib.ConjunctiveGraph): The full RDF graph of this nanopublication (quads)
        assertion (rdflib.Graph): The part of the graph describing the assertion.
        pubinfo (rdflib.Graph): The part of the graph describing the publication information.
        provenance (rdflib.Graph): The part of the graph describing the provenance.
        source_uri (str): The URI of the nanopublication that this Publication represents (if applicable)
        introduces_concept (rdflib.BNode): The concept that is introduced by this Publication (if applicable)
    """

    def __init__(
        self,
        source_uri: str = None,
        assertion: Graph = Graph(),
        provenance: Graph = Graph(),
        pubinfo: Graph = Graph(),
        rdf: Union[ConjunctiveGraph, Path] = None,
        introduces_concept: BNode = None,
        conf: NanopubConf = NanopubConf(),
    ) -> None:
        self._profile = conf.profile
        self._source_uri = source_uri
        self._concept_uri = None
        self._conf = deepcopy(conf)
        self._metadata = NanopubMetadata()
        self._published = False
        if self._conf.use_test_server:
            self._conf.use_server = NANOPUB_TEST_SERVER
        if self._conf.use_server == NANOPUB_TEST_SERVER:
            self._conf.use_test_server = True

        # Get the nanopub RDF depending on how it is provided:
        # source URI, rdflib graph, or file
        if source_uri:
            # If source URI provided we retrieve the nanopub from the servers
            r = requests.get(source_uri + "." + NANOPUB_FETCH_FORMAT)
            if not r.ok and self._conf.use_test_server:
                nanopub_id = source_uri.rsplit("/", 1)[-1]
                uri_test = NANOPUB_TEST_SERVER + nanopub_id
                r = requests.get(uri_test + "." + NANOPUB_FETCH_FORMAT)
            r.raise_for_status()
            self._rdf = self._preformat_graph(ConjunctiveGraph())
            self._rdf.parse(data=r.text, format=NANOPUB_FETCH_FORMAT)

            self._metadata = extract_np_metadata(self._rdf)
        else:
            # if provided as rdflib graph, or file
            if isinstance(rdf, ConjunctiveGraph):
                self._rdf = self._preformat_graph(rdf)
                self._metadata = extract_np_metadata(self._rdf)
            elif isinstance(rdf, Path):
                self._rdf = self._preformat_graph(ConjunctiveGraph())
                self._rdf.parse(rdf)
                self._metadata = extract_np_metadata(self._rdf)
            else:
                self._rdf = self._preformat_graph(ConjunctiveGraph())

        # Instantiate the different graph from the provided RDF (trig/nquads)
        self._head = Graph(self._rdf.store, self._metadata.head)
        self._assertion = Graph(self._rdf.store, self._metadata.assertion)
        self._provenance = Graph(self._rdf.store, self._metadata.provenance)
        self._pubinfo = Graph(self._rdf.store, self._metadata.pubinfo)

        self._assertion += assertion
        self._provenance += provenance
        self._pubinfo += pubinfo

        # Concatenate prefixes declarations from all provided graphs in the main graph
        for user_rdf in [assertion, provenance, pubinfo]:
            if user_rdf is not None:
                for prefix, namespace in user_rdf.namespaces():
                    self._rdf.bind(prefix, namespace)

        # Add Head graph if the nanopub was not provided as trig/nquads
        if not rdf and not source_uri:
            self._head.add((
                self._metadata.namespace[""],
                RDF.type,
                NP.Nanopublication
            ))
            self._head.add((
                self._metadata.namespace[""],
                NP.hasAssertion,
                self._assertion.identifier,
            ))
            self._head.add((
                self._metadata.namespace[""],
                NP.hasProvenance,
                self._provenance.identifier,
            ))
            self._head.add((
                self._metadata.namespace[""],
                NP.hasPublicationInfo,
                self._pubinfo.identifier,
            ))

        # Add triples to the nanopub depending on the provided NanopuConf (e.g. creator, date)
        self._validate_nanopub_arguments(
            introduces_concept=introduces_concept,
            derived_from=self._conf.derived_from,
            assertion_attributed_to=self._conf.assertion_attributed_to,
            attribute_assertion_to_profile=self._conf.attribute_assertion_to_profile,
            # publication_attributed_to=publication_attributed_to,
        )
        self._handle_generated_at_time(
            self._conf.add_pubinfo_generated_time,
            self._conf.add_prov_generated_time
        )
        assertion_attributed_to = self._conf.assertion_attributed_to
        if self._conf.attribute_assertion_to_profile:
            assertion_attributed_to = rdflib.URIRef(self.profile.orcid_id)
        self._handle_assertion_attributed_to(assertion_attributed_to)
        self._handle_publication_attributed_to(
            self._conf.attribute_publication_to_profile,
            self._conf.publication_attributed_to
        )
        self._handle_derived_from(derived_from=self._conf.derived_from)


    def _preformat_graph(self, g: ConjunctiveGraph) -> ConjunctiveGraph:
        """Add a few default namespaces"""
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
        self._metadata = extract_np_metadata(signed_g)
        if self._metadata.trusty:
            self._source_uri = str(self._metadata.np_uri)
        # self._source_uri = self.get_source_uri_from_graph
        self._rdf = signed_g
        self._head = Graph(self._rdf.store, self._metadata.head)
        self._assertion = Graph(self._rdf.store, self._metadata.assertion)
        self._provenance = Graph(self._rdf.store, self._metadata.provenance)
        self._pubinfo = Graph(self._rdf.store, self._metadata.pubinfo)


    def sign(self) -> None:
        """Sign a Nanopub object"""
        if len(self.rdf) > MAX_TRIPLES_PER_NANOPUB:
            raise MalformedNanopubError(f"Nanopublication contains {len(self.rdf)} triples, which is more than the {MAX_TRIPLES_PER_NANOPUB} authorized")
        if not self._conf.profile:
            raise ProfileError("Profile not available, cannot sign the nanopub")
        if self._metadata.signature:
            raise MalformedNanopubError(f"The nanopub have already been signed: {self.source_uri}")

        if self.is_valid:
            signed_g = add_signature(self.rdf, self._conf.profile, self._metadata.namespace, URIRef(str(self._pubinfo.identifier)))
            self.update_from_signed(signed_g)
            log.info(f"Signed {self.source_uri}")
        else:
            raise MalformedNanopubError("The nanopub is not valid, cannot sign it")


    def publish(self) -> None:
        """Publish a Nanopub object"""
        if not self.source_uri:
            self.sign()

        publish_graph(self.rdf, use_server=self._conf.use_server)
        log.info(f'Published {self.source_uri} to {self._conf.use_server}')
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


    def update(self, publish=True) -> None:
        """Re-publish an updated Nanopub object"""
        self._pubinfo.add((
            URIRef(self.source_uri),
            NPX.supersedes,
            URIRef(self.source_uri),
        ))
        self._pubinfo.remove((
            self._metadata.sig_uri,
            None,
            None,
        ))
        self._metadata = extract_np_metadata(self._rdf)
        print(self._metadata)
        if publish:
            self.publish()
        else:
            self.sign()



    def store(self, filepath: Path, format: str = 'trig') -> None:
        """Store the Nanopub object at the given path"""
        self._rdf.serialize(filepath, format=format)


    @property
    def has_valid_signature(self) -> bool:
        verify_signature(self._rdf, self._metadata.namespace)
        return True

    @property
    def has_valid_trusty(self) -> bool:
        verify_trusty(self._rdf, self.source_uri, self._metadata.namespace)
        return True

    @property
    def is_valid(self) -> bool:
        """Check if a nanopublication is valid"""
        np_meta = extract_np_metadata(self._rdf)
        np_uri = np_meta.np_uri

        # Check if any of the graph is empty
        if len(self._head) < 1:
            raise MalformedNanopubError("The Head graph is empty")
        if len(self._assertion) < 1:
            raise MalformedNanopubError("The assertion graph is empty")
        if len(self._provenance) < 1:
            raise MalformedNanopubError("The provenance graph is empty")
        if len(self._pubinfo) < 1:
            raise MalformedNanopubError("The pubinfo graph is empty")

        # Check exactly 4 graphs
        graph_count = 0
        for c in self._rdf.contexts():
            if len(list(self._rdf.quads((None, None, None, c)))) > 0:
                graph_count += 1
        if graph_count != 4:
            raise MalformedNanopubError(f"\033[1mToo many graphs found\033[0m in the provided RDF: {graph_count}. A Nanopub should have only 4 graphs (Head, assertion, provenance, pubinfo)")

        found_prov = False
        for s, p, o in self._provenance:
            if str(s) == str(np_meta.assertion):
                found_prov = True
                break
        if not found_prov:
            raise MalformedNanopubError(f"The provenance graph should contain at least one triple with the assertion graph URI as subject: \033[1m{np_meta.assertion}\033[0m")

        found_pubinfo = False
        for s, p, o in self._pubinfo:
            if str(s) == str(np_uri) or str(s) == str(np_meta.namespace):
                found_pubinfo = True
                break
        if not found_pubinfo:
            raise MalformedNanopubError(f"The pubinfo graph should contain at least one triple that has the nanopub URI as subject: \033[1m{np_uri}\033[0m")

        # print(self)
        # if len(self._head) != 4:
        #     raise MalformedNanopubError(f"Too many triples in the nanopublication Head graph: {len(self._head)} instead of 4")

        # TODO: add more checks for trusty and signature
        # if self._metadata.signature:
        #     if self.has_valid_signature is False:
        #         raise MalformedNanopubError("The nanopub is not valid")
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
    def metadata(self):
        return self._metadata

    @property
    def conf(self):
        return self._conf

    @conf.setter
    def conf(self, value):
        self._conf = value

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
    def namespace(self):
        return self._metadata.namespace

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
        np_sig = extract_np_metadata(self._rdf)
        if np_sig.public_key:
            return np_sig.public_key
        return None


    @property
    def is_test_publication(self) -> bool:
        return self._conf.use_test_server


    def __str__(self) -> str:
        s = ""
        if self._source_uri:
            s += f"Nanopub URI: \033[1m{self._source_uri}\033[0m\n"
        np_serialized = self._rdf.serialize(format='trig')
        # In rdflib v5, .serialize() returns a bytes object that needs to be decoded.
        # (rdflib 6+ returns a str)
        if isinstance(np_serialized, bytes):
            np_serialized = np_serialized.decode('utf-8')
        s += np_serialized
        return s


    def _handle_generated_at_time(
        self, add_pubinfo_generated_time: bool, add_prov_generated_time: bool
    ) -> None:
        """Handler for `Nanopub` constructor."""
        creationtime = rdflib.Literal(datetime.now(), datatype=XSD.dateTime)
        if add_pubinfo_generated_time:
            self._pubinfo.add(
                (self._metadata.namespace[""], PROV.generatedAtTime, creationtime)
            )
        if add_prov_generated_time:
            self._provenance.add(
                (
                    self._assertion.identifier,
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
                    self._assertion.identifier,
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
                    self._metadata.namespace[""],
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
                self._provenance.add((
                    self._assertion.identifier,
                    PROV.wasDerivedFrom,
                    derived_from_uri,
                ))

    def _handle_introduces_concept(self, introduces_concept: Union[BNode, URIRef]):
        """Handler for `Nanopub` constructor."""
        if introduces_concept:
            introduces_concept = self._metadata.namespace[str(introduces_concept)]
            self._pubinfo.add(
                (self._metadata.namespace[""], NPX.introduces, introduces_concept)
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
        if self._pubinfo:
            if (
                introduces_concept
                and (None, NPX.introduces, None) in self._pubinfo
            ):
                raise MalformedNanopubError(
                    "The pubinfo_rdf that you passed already contains the "
                    "npx:introduces predicate, so you cannot also use the "
                    "introduces_concept argument"
                )
            # if (None, PROV.wasAttributedTo, None) in self._pubinfo:
            #     raise MalformedNanopubError(
            #         "The pubinfo_rdf that you passed should not contain the "
            #         "prov:wasAttributedTo predicate. If you wish to change "
            #         "who the publication is attributed to, please use the "
            #         "publication_attributed_to argument instead. By default "
            #         "this is the ORCID set in your profile, but you can set "
            #         "it to another URI if desired."
            #     )

    # TODO: we might to use it to convert blank nodes directly as URI
    # instead of having a hack to normalize URIs starting with _
    # def _replace_blank_nodes(self, rdf: ConjunctiveGraph) -> ConjunctiveGraph:
    #     """Replace blank nodes.
    #       Replace any blank nodes in the supplied RDF with a corresponding uri in the
    #     dummy_namespace.'Blank nodes' here refers specifically to rdflib.term.BNode objects. When
    #     publishing, the dummy_namespace is replaced with the URI of the actual nanopublication.
    #       For example, if the nanopub's URI is www.purl.org/ABC123 then the blank node will be
    #     replaced with a concrete URIRef of the form www.purl.org/ABC123#blanknodename where
    #     'blanknodename' is the name of the rdflib.term.BNode object.
    #       This is to solve the problem that a user may wish to use the nanopublication to introduce
    #     a new concept. This new concept needs its own URI (it cannot simply be given the
    #     nanopublication's URI), but it should still lie within the space of the nanopub.
    #     Furthermore, the URI the nanopub is published to is not known ahead of time.
    #     """
    #     for s, p, o in rdf:
    #         if isinstance(s, BNode):
    #             rdf.remove((s, p, o))
    #             s = self._metadata.namespace[f"_{str(s)}"]
    #             rdf.add((s, p, o))
    #         if isinstance(o, BNode):
    #             rdf.remove((s, p, o))
    #             o = self._metadata.namespace[f"_{str(o)}"]
    #             rdf.add((s, p, o))
    #     return rdf
