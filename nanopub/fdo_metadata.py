from rdflib import Graph, URIRef, Literal
from typing import Optional
from rdflib.namespace import RDFS
from nanopub.namespaces import HDL
from nanopub.constants import FDO_PROFILE_HANDLE

class FdoMetadata:
    """
    EXPERIMENTAL: This class is experimental and may change or be removed in future versions.
    """
    def __init__(self, nanopub: Graph):
        self.id: Optional[str] = None
        self.tuples: dict[URIRef, Literal | URIRef] = {}

        for s, p, o in nanopub:
            if p == HDL[FDO_PROFILE_HANDLE] and self.id is None:
                self.id = self.extract_handle(s)
            self.tuples[p] = o

        if self.id is None:
            raise ValueError("Missing required FDO profile statement")

    def extract_handle(self, subject: URIRef) -> str:
        return str(subject).split("/")[-1] 

    def get_statements(self) -> list[tuple[URIRef, URIRef, Literal | URIRef]]:
        """
        Returns the metadata as a list of RDF triples.
        """
        subject = URIRef(f"https://hdl.handle.net/{self.id}")
        return [(subject, p, o) for p, o in self.tuples.items()]

    def get_graph(self) -> Graph:
        """
        Returns the metadata as an rdflib.Graph.
        """
        g = Graph()
        subject = URIRef(f"https://hdl.handle.net/{self.id}")
        for p, o in self.tuples.items():
            g.add((subject, p, o))
        return g

    def get_profile(self) -> Optional[URIRef]:
        val = self.tuples.get(HDL[FDO_PROFILE_HANDLE])
        return URIRef(val) if val else None

    def get_label(self) -> Optional[str]:
        val = self.tuples.get(RDFS.label)
        return str(val) if val else None

    def get_id(self) -> Optional[str]:
        return self.id
