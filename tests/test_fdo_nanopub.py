import pytest
import rdflib
from rdflib import RDF, RDFS
from nanopub.namespaces import HDL, FDOF, NPX
from nanopub.fdo_nanopub import FDONanopub, to_hdl_uri 

FAKE_HANDLE = "21.T11966/test"
FAKE_URI = HDL[FAKE_HANDLE]
FAKE_LABEL = "Test Object"
FAKE_TYPE_JSON = '{"@type": "Dataset"}'
FAKE_STATUS = "active"
FAKE_ATTR_VALUE = rdflib.Literal("some value")
FAKE_ATTR_LABEL = "Test Attribute"
FDO_PROFILE_HANDLE = HDL['21.T11966/FdoProfile']


@pytest.mark.parametrize("fdo_id", [FAKE_HANDLE, HDL[FAKE_HANDLE]])
def test_initial_fdo_triples(fdo_id):
    fdo = FDONanopub(fdo_id, FAKE_LABEL)
    fdo_uri = to_hdl_uri(fdo_id)

    assert (fdo_uri, RDF.type, FDOF.FAIRDigitalObject) in fdo.assertion
    assert (fdo_uri, RDFS.label, rdflib.Literal(FAKE_LABEL)) in fdo.assertion
    assert (fdo_uri, FDOF.hasMetadata, fdo.metadata.np_uri) in fdo.assertion
    assert (fdo.metadata.np_uri, RDFS.label, rdflib.Literal(f"FAIR Digital Object: {FAKE_LABEL}")) in fdo.pubinfo
    assert (fdo.metadata.np_uri, NPX.introduces, fdo_uri) in fdo.pubinfo

@pytest.mark.parametrize("fdo_profile", [FAKE_HANDLE, HDL[FAKE_HANDLE]])
def test_add_fdo_profile(fdo_profile):
    fdo = FDONanopub(FAKE_HANDLE, FAKE_LABEL)
    uri = to_hdl_uri(fdo_profile)
    fdo.add_fdo_profile(fdo_profile)
    assert (fdo.fdo_uri, fdo.FDO_PROFILE_HANDLE, rdflib.Literal(uri)) in fdo.assertion
    assert (fdo.FDO_PROFILE_HANDLE, RDFS.label, rdflib.Literal("FdoProfile")) in fdo.pubinfo

@pytest.mark.parametrize("data_ref", [FAKE_HANDLE, HDL[FAKE_HANDLE]])
def test_add_fdo_data_ref(data_ref):
    fdo = FDONanopub(FAKE_HANDLE, FAKE_LABEL)
    uri = to_hdl_uri(data_ref)
    fdo.add_fdo_data_ref(data_ref)
    assert (fdo.fdo_uri, fdo.DATA_REF_HANDLE, uri) in fdo.assertion
    assert (fdo.DATA_REF_HANDLE, RDFS.label, rdflib.Literal("DataRef")) in fdo.pubinfo

@pytest.mark.parametrize("service_uri", [FAKE_HANDLE, HDL[FAKE_HANDLE]])
def test_add_fdo_service(service_uri):
    fdo = FDONanopub(FAKE_HANDLE, FAKE_LABEL)
    uri = to_hdl_uri(service_uri)
    fdo.add_fdo_service(service_uri)
    assert (fdo.fdo_uri, fdo.FDO_SERVICE_HANDLE, uri) in fdo.assertion
    assert (fdo.FDO_SERVICE_HANDLE, RDFS.label, rdflib.Literal("FdoService")) in fdo.pubinfo

@pytest.mark.parametrize("attr_HANDLE", [FAKE_HANDLE, HDL[FAKE_HANDLE]])
def test_add_attribute_and_label(attr_HANDLE):
    fdo = FDONanopub(FAKE_HANDLE, FAKE_LABEL)
    uri = to_hdl_uri(attr_HANDLE)
    fdo.add_attribute(attr_HANDLE, FAKE_ATTR_VALUE)
    fdo.add_attribute_label(attr_HANDLE, FAKE_ATTR_LABEL)
    assert (fdo.fdo_uri, uri, FAKE_ATTR_VALUE) in fdo.assertion
    assert (uri, RDFS.label, rdflib.Literal(FAKE_ATTR_LABEL)) in fdo.pubinfo

def test_add_fdo_type():
    fdo = FDONanopub(FAKE_HANDLE, FAKE_LABEL)
    fdo.add_fdo_type(FAKE_TYPE_JSON)
    # Related to https://github.com/RDFLib/rdflib/issues/1830
    # assert (fdo.fdo_uri, fdo.FDO_TYPE_HANDLE, rdflib.Literal(FAKE_TYPE_JSON, datatype=XSD.string)) in fdo.assertion
    assert (fdo.FDO_TYPE_HANDLE, RDFS.label, rdflib.Literal("FdoType")) in fdo.pubinfo

def test_add_fdo_status():
    fdo = FDONanopub(FAKE_HANDLE, FAKE_LABEL)
    fdo.add_fdo_status(FAKE_STATUS)
    assert (fdo.fdo_uri, fdo.FDO_STATUS_HANDLE, rdflib.Literal(FAKE_STATUS)) in fdo.assertion
    assert (fdo.FDO_STATUS_HANDLE, RDFS.label, rdflib.Literal("FdoStatus")) in fdo.pubinfo
