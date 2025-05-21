from .nanopub import Nanopub
import rdflib
from rdflib.namespace import RDF, RDFS, XSD
from nanopub.namespaces import HDL, FDOF, NPX
from nanopub.constants import FDO_PROFILE_HANDLE, FDO_DATA_REF_HANDLE

def to_hdl_uri(value):
    if isinstance(value, rdflib.URIRef): 
        return value
    elif isinstance(value, str) and not value.startswith('http'):
        return HDL[value] 
    else:
        raise ValueError(f"Invalid value: {value}")

class FDONanopub(Nanopub):
    """
    EXPERIMENTAL: This class is experimental and may change or be removed in future versions.
    """
    
    def __init__(self, fdo_id: rdflib.URIRef | str, label: str, fdo_profile: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fdo_uri = to_hdl_uri(fdo_id)  
        self.fdo_profile = fdo_profile
        self._init_core_fdo_triples(label)

    def _init_core_fdo_triples(self, label: str):
        self.assertion.add((self.fdo_uri, RDF.type, FDOF.FAIRDigitalObject))
        self.assertion.add((self.fdo_uri, RDFS.label, rdflib.Literal(label)))
        self.assertion.add((self.fdo_uri, FDOF.hasMetadata, self.metadata.np_uri))
        if self.fdo_profile:
            profile_uri = to_hdl_uri(self.fdo_profile)
            self.assertion.add((self.fdo_uri, FDOF.hasProfile, profile_uri))

        self.pubinfo.add((self.metadata.np_uri, RDFS.label, rdflib.Literal(f"FAIR Digital Object: {label}")))
        self.pubinfo.add((self.metadata.np_uri, NPX.introduces, self.fdo_uri))

    def add_fdo_profile(self, profile_uri: rdflib.URIRef):
        profile_uri = to_hdl_uri(profile_uri)
        self.assertion.add((self.fdo_uri, HDL[FDO_PROFILE_HANDLE], rdflib.Literal(profile_uri)))
        self.pubinfo.add((HDL[FDO_PROFILE_HANDLE], RDFS.label, rdflib.Literal("FdoProfile")))

    def add_fdo_data_ref(self, target_uri: rdflib.URIRef):
        target_uri = to_hdl_uri(target_uri)  
        self.assertion.add((self.fdo_uri, HDL[FDO_DATA_REF_HANDLE], target_uri))
        self.pubinfo.add((HDL[FDO_DATA_REF_HANDLE], RDFS.label, rdflib.Literal("DataRef")))

    def add_attribute(self, attr_HANDLE: rdflib.URIRef, value: rdflib.Literal):
        attr_HANDLE = to_hdl_uri(attr_HANDLE) 
        self.assertion.add((self.fdo_uri, attr_HANDLE, rdflib.Literal(value)))

    def add_attribute_label(self, attr_HANDLE: rdflib.URIRef, label: str):
        attr_HANDLE = to_hdl_uri(attr_HANDLE) 
        self.pubinfo.add((attr_HANDLE, RDFS.label, rdflib.Literal(label)))

