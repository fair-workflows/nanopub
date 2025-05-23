from rdflib import Graph, URIRef, Literal
from typing import Optional, Union
from rdflib.namespace import RDFS
from nanopub.namespaces import HDL, FDOF
from nanopub.constants import FDO_PROFILE_HANDLE


class FdoMetadata:
    """
    EXPERIMENTAL: This class is experimental and may change or be removed in future versions.
    """

    def __init__(self, nanopub: Optional[Graph] = None):
        self.id: Optional[str] = None
        self.tuples: dict[URIRef, Union[Literal, URIRef]] = {}

        if nanopub:
            for s, p, o in nanopub:
                if p == FDOF.hasFdoProfile and self.id is None:
                    self.id = self.extract_handle(s)
                self.tuples[p] = o

            if self.id is None:
                raise ValueError("Missing required FDO profile statement")

    def extract_handle(self, subject: URIRef) -> str:
        return str(subject).split("/")[-1]

    def get_statements(self) -> list[tuple[URIRef, URIRef, Union[Literal, URIRef]]]:
        """
        Returns the metadata as a list of RDF triples.
        """
        if not self.id:
            raise ValueError("FDO ID is not set")
        subject = URIRef(f"https://hdl.handle.net/{self.id}")
        return [(subject, p, o) for p, o in self.tuples.items()]

    def get_graph(self) -> Graph:
        """
        Returns the metadata as an rdflib.Graph.
        """
        g = Graph()
        for s, p, o in self.get_statements():
            g.add((s, p, o))
        return g

    def get_profile(self) -> Optional[URIRef]:
        val = self.tuples.get(FDOF.hasFdoProfile)
        return URIRef(val) if val else None

    def get_label(self) -> Optional[str]:
        val = self.tuples.get(RDFS.label)
        return str(val) if val else None

    def get_id(self) -> Optional[str]:
        return self.id

    def set_id(self, handle: str) -> None:
        self.id = handle

    def set_label(self, label: str) -> None:
        self.tuples[RDFS.label] = Literal(label)

    def set_profile(self, uri: Union[str, URIRef]) -> None:
        self.tuples[FDOF.hasFdoProfile] = URIRef(uri)

    def set_property(self, predicate: Union[str, URIRef], value: Union[str, URIRef, Literal]) -> None:
        pred = URIRef(predicate)
        obj = URIRef(value) if isinstance(value, str) and value.startswith("http") else Literal(value)
        self.tuples[pred] = obj

    def copy(self) -> "FdoMetadata":
        new_md = FdoMetadata()
        new_md.id = self.id
        new_md.tuples = self.tuples.copy()
        return new_md
