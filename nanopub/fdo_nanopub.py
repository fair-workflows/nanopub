import rdflib
from rdflib.namespace import RDF, RDFS, XSD

from nanopub.namespaces import FDOF, HDL, NPX

from .nanopub import Nanopub


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
    DATA_REF_HANDLE = HDL["21.T11966/06a6c27e3e2ef27779ec"]
    FDO_TYPE_HANDLE = HDL["21.T11966/06fae297d104953b2eaa"]
    FDO_STATUS_HANDLE = HDL["21.T11966/143d58e30d417a2cb75d"]
    FDO_PROFILE_HANDLE = HDL["21.T11966/4ee0ae648b243f49850f"]
    FDO_SERVICE_HANDLE = HDL["21.T11966/b5b58656b1fa5aff0505"]
    FDO_PROFILE_HANDLE= HDL['21.T11966/FdoProfile']

    def __init__(self, fdo_id: rdflib.URIRef | str, label: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fdo_uri = to_hdl_uri(fdo_id)
        self._init_core_fdo_triples(label)

    def _init_core_fdo_triples(self, label: str):
        self.assertion.add((self.fdo_uri, RDF.type, FDOF.FAIRDigitalObject))
        self.assertion.add((self.fdo_uri, RDFS.label, rdflib.Literal(label)))
        self.assertion.add((self.fdo_uri, FDOF.hasMetadata, self.metadata.np_uri))

        self.pubinfo.add((self.metadata.np_uri, RDFS.label, rdflib.Literal(f"FAIR Digital Object: {label}")))
        self.pubinfo.add((self.metadata.np_uri, NPX.introduces, self.fdo_uri))

    def add_fdo_profile(self, profile_uri: rdflib.URIRef):
        profile_uri = to_hdl_uri(profile_uri)
        self.assertion.add((self.fdo_uri, self.FDO_PROFILE_HANDLE, rdflib.Literal(profile_uri)))
        self.pubinfo.add((self.FDO_PROFILE_HANDLE, RDFS.label, rdflib.Literal("FdoProfile")))

    def add_fdo_data_ref(self, target_uri: rdflib.URIRef):
        target_uri = to_hdl_uri(target_uri)
        self.assertion.add((self.fdo_uri, self.DATA_REF_HANDLE, target_uri))
        self.pubinfo.add((self.DATA_REF_HANDLE, RDFS.label, rdflib.Literal("DataRef")))

    def add_fdo_type(self, type_json: str):
        self.assertion.add((self.fdo_uri, self.FDO_TYPE_HANDLE, rdflib.Literal(type_json, datatype=XSD.string)))
        self.pubinfo.add((self.FDO_TYPE_HANDLE, RDFS.label, rdflib.Literal("FdoType")))

    def add_fdo_status(self, status: str):
        self.assertion.add((self.fdo_uri, self.FDO_STATUS_HANDLE, rdflib.Literal(status)))
        self.pubinfo.add((self.FDO_STATUS_HANDLE, RDFS.label, rdflib.Literal("FdoStatus")))

    def add_fdo_service(self, service_uri: rdflib.URIRef):
        service_uri = to_hdl_uri(service_uri)
        self.assertion.add((self.fdo_uri, self.FDO_SERVICE_HANDLE, service_uri))
        self.pubinfo.add((self.FDO_SERVICE_HANDLE, RDFS.label, rdflib.Literal("FdoService")))

    def add_attribute(self, attr_HANDLE: rdflib.URIRef, value: rdflib.Literal):
        attr_HANDLE = to_hdl_uri(attr_HANDLE)
        self.assertion.add((self.fdo_uri, attr_HANDLE, value))

    def add_attribute_label(self, attr_HANDLE: rdflib.URIRef, label: str):
        attr_HANDLE = to_hdl_uri(attr_HANDLE)
        self.pubinfo.add((attr_HANDLE, RDFS.label, rdflib.Literal(label)))
