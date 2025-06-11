from nanopub import Nanopub
import rdflib
from rdflib.namespace import RDF, RDFS, XSD
from nanopub.namespaces import HDL, FDOF, NPX, FDOC
from nanopub.constants import FDO_PROFILE_HANDLE, FDO_DATA_REF_HANDLE


def to_hdl_uri(value):
    if isinstance(value, rdflib.URIRef): 
        return value
    elif isinstance(value, str) and not value.startswith('http'):
        return HDL[value] 
    else:
        raise ValueError(f"Invalid value: {value}")


class FdoNanopub(Nanopub):
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
            self.assertion.add((self.fdo_uri, FDOC.hasFdoProfile, profile_uri))

        self.pubinfo.add((self.metadata.np_uri, RDFS.label, rdflib.Literal(f"FAIR Digital Object: {label}")))
        self.pubinfo.add((self.metadata.np_uri, NPX.introduces, self.fdo_uri))
        
    @classmethod
    def handle_to_nanopub(cls, handle: str, **kwargs) -> "FdoNanopub":
        from nanopub.fdo.retrieve import resolve_handle_metadata
        data = resolve_handle_metadata(handle)
        values = data.get("values", [])

        label = None
        profile = None
        data_ref = None
        other_attributes = []

        for entry in values:
            entry_type = entry.get("type")
            entry_value = entry.get("data", {}).get("value")

            if entry_type == "HS_ADMIN":
                continue
            elif entry_type == "name":
                label = entry_value
            elif entry_type == FDO_PROFILE_HANDLE:
                profile = entry_value
            elif entry_type == FDO_DATA_REF_HANDLE:
                data_ref = entry_value
            else:
                other_attributes.append((entry_type, entry_value))

        np = cls(fdo_id=handle, label=label or handle, fdo_profile=profile, **kwargs)

        if data_ref:
            np.add_fdo_data_ref(data_ref)

        for attr_type, val in other_attributes:
            np.add_attribute(attr_type, val)

        return np
      
    @classmethod
    def create_with_fdo_iri(cls, fdo_iri, profile_iri, label):
        fdo_uri = rdflib.URIRef(fdo_iri) if not isinstance(fdo_iri, rdflib.URIRef) else fdo_iri
        profile_uri = rdflib.URIRef(profile_iri) if not isinstance(profile_iri, rdflib.URIRef) else profile_iri
        return cls(fdo_id=fdo_uri, label=label, fdo_profile=profile_uri)

    def add_fdo_profile(self, profile_uri: rdflib.URIRef | str):
        profile_uri = to_hdl_uri(profile_uri)
        self.assertion.add((self.fdo_uri, FDOC.hasFdoProfile, profile_uri))
        self.pubinfo.add((HDL[FDO_PROFILE_HANDLE], RDFS.label, rdflib.Literal("FdoProfile")))

    def add_fdo_data_ref(self, data_ref: rdflib.Literal | str):
        target_uri = to_hdl_uri(data_ref)  
        self.assertion.add((self.fdo_uri, FDOF.isMaterializedBy, target_uri))
        self.pubinfo.add((HDL[FDO_DATA_REF_HANDLE], RDFS.label, rdflib.Literal("DataRef")))

    def add_attribute(self, attr_handle: rdflib.URIRef | str, value: rdflib.Literal | str):
        attr_handle = to_hdl_uri(attr_handle) 
        self.assertion.add((self.fdo_uri, attr_handle, rdflib.Literal(value)))

    def add_attribute_label(self, attr_handle: rdflib.URIRef | str, label: str):
        attr_handle = to_hdl_uri(attr_handle) 
        self.pubinfo.add((attr_handle, RDFS.label, rdflib.Literal(label)))
