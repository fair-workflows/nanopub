from typing import List

from rdflib import Literal, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, RDFS, XSD

from nanopub.config import NanopubConfig
from nanopub.definitions import DUMMY_NAMESPACE, DUMMY_URI, MAX_NP_PER_INDEX, log
from nanopub.namespaces import NPX, PAV
from nanopub.nanopub import Nanopub


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
        config: NanopubConfig,
        np_list: List[str],
        title: str,
        description: str,
        creation_time: str,
        creators: List[str],
        see_also: str = None,
        top_level: bool = False,
    ) -> None:
        config.add_prov_generated_time = False
        config.add_pubinfo_generated_time = True
        config.attribute_publication_to_profile = True
        super().__init__(
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


def create_nanopub_index(
    config: NanopubConfig,
    np_list: List[str],
    title: str,
    description: str,
    creation_time: str,
    creators: List[str],
    see_also: str = None,
    # pub_list: List[Nanopublication] = [],
    publish: bool = False,
) -> List[Nanopub]:
    """Create a Nanopub index.

    Publish a list of nanopub URIs in a Nanopub Index

    Args:
        np_list: List of nanopub URIs
        title: Title of the Nanopub Index
        description: Description of the Nanopub Index
        creation_time: Creation time of the Nanopub Index, in format YYYY-MM-DDThh-mm-ss
        creators: List of the ORCID of the creators of the Nanopub Index
        see_also: A URL to a page with further information on the Nanopub Index
    """
    pub_list = []
    for i in range(0, len(np_list), MAX_NP_PER_INDEX):
        np_chunk = np_list[i:i + MAX_NP_PER_INDEX]
        pub = NanopubIndex(
            config,
            np_chunk,
            title,
            description,
            creation_time,
            creators,
            see_also,
            top_level=False
        )
        if publish:
            pub.publish()
            log_msg = "Published"
        else:
            pub.sign()
            log_msg = "Signed"
        pub_uri = pub.source_uri
        log.info(f"{log_msg} Nanopub Index: {pub_uri}")

        pub_list.append(pub_uri)

    if len(pub_list) > 1:
        toplevel_pub = NanopubIndex(
            config,
            pub_list,
            title,
            description,
            creation_time,
            creators,
            see_also,
            top_level=True
        )

        if publish:
            toplevel_pub.publish()
            log_msg = "Published"
        else:
            toplevel_pub.sign()
            log_msg = "Signed"
        toplevel_uri = toplevel_pub.source_uri
        log.info(f"{log_msg} Nanopub Index: {toplevel_uri}")

        pub_list.append(toplevel_uri)

    return pub_list
