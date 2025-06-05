import json
import pytest
from unittest.mock import patch, MagicMock
from nanopub.fdo.validate import validate_fdo_nanopub
from nanopub.fdo.fdo_nanopub import FdoNanopub, to_hdl_uri
from rdflib import URIRef
from nanopub.namespaces import HDL, FDOF, NPX

HANDLE_METADATA = {
    "responseCode": 1,
    "handle": "21.T11966/82045bd97a0acce88378",
    "values": [
        {
            "index": 2,
            "type": "21.T11966/FdoProfile",
            "data": {"format": "string", "value": "21.T11966/996c38676da9ee56f8ab"},
        },
        {
            "index": 3,
            "type": "21.T11966/JsonSchema",
            "data": {
                "format": "string",
                "value": json.dumps({
                    "$ref": "https://example.org/schema/fdo.json"
                }),
            },
        },
        {
            "index": 1,
            "type": "name",
            "data": {"format": "string", "value": "Example FDO"},
        },
    ],
}

JSON_SCHEMA = {
    "type": "object",
    "required": [
      "21.T11966/FdoProfile",
      "21.T11966/b5b58656b1fa5aff0505"
    ]
}

@pytest.fixture
def valid_fdo_nanopub():
    fdonp = FdoNanopub(fdo_id="21.T11966/82045bd97a0acce88378", label="", fdo_profile="21.T11966/996c38676da9ee56f8ab")
    return fdonp

@patch("nanopub.fdo_ops.requests.get")
def test_validate_fdo_nanopub_success(mock_get, valid_fdo_nanopub):
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: HANDLE_METADATA),
        MagicMock(status_code=200, json=lambda: JSON_SCHEMA),
    ]

    assert validate_fdo_nanopub(valid_fdo_nanopub) is True

@patch("nanopub.fdo_ops.requests.get")
def test_handle_to_nanopub(mock_get):
    mock_get.return_value = MagicMock(status_code=200, json=lambda: HANDLE_METADATA)
    fdonp = FdoNanopub.handle_to_nanopub("21.T11966/82045bd97a0acce88378")

    assert isinstance(fdonp, FdoNanopub)
    assert fdonp.fdo_uri == to_hdl_uri("21.T11966/82045bd97a0acce88378")
    assert fdonp.fdo_profile == "21.T11966/996c38676da9ee56f8ab"

@patch("nanopub.fdo_ops.requests.get")
def test_validate_fdo_nanopub_failure(mock_get, valid_fdo_nanopub):
    incomplete_handle_metadata = {
        "responseCode": 1,
        "handle": "21.T11966/82045bd97a0acce88378",
        "values": [
            {
                "index": 2,
                "type": "21.T11966/FdoProfile",
                "data": {"format": "string", "value": "21.T11966/996c38676da9ee56f8ab"},
            },
            {
                "index": 1,
                "type": "name",
                "data": {"format": "string", "value": "Example FDO"},
            },
        ],
    }

    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: incomplete_handle_metadata),
        MagicMock(status_code=200, json=lambda: JSON_SCHEMA),
    ]

    assert validate_fdo_nanopub(valid_fdo_nanopub) is False
    


FDO_HANDLE = "21.T11966/123456789abcdef"
DATAREF_HANDLE = "21.T11967/83d2b3f39034b2ac78cd"
HDL_PREFIX = "https://hdl.handle.net/"
FDO_NAMESPACE = "https://w3id.org/fdo#"

HANDLE_METADATA_WITH_DATAREF =  {
    "responseCode": 1,
    "handle": "21.T11966/82045bd97a0acce88378",
    "values": [
        {
            "index": 1,
            "type": "21.T11966/name",
            "data": {"format": "string", "value": "FDO with DataRef"},
        },
        {
            "index": 2,
            "type": "21.T11966/FdoProfile",
            "data": {"format": "string", "value": "21.T11966/996c38676da9ee56f8ab"},
        },
        {
            "index": 3,
            "type": "21.T11966/JsonSchema",
            "data": {
                "format": "string",
                "value": json.dumps({
                    "$ref": "https://example.org/schema/fdo.json"
                }),
            },
        },
        {
            "index": 4,
            "type": "21.T11966/06a6c27e3e2ef27779ec", 
            "data": {"format": "string", "value": DATAREF_HANDLE},
        },
    ],
}

@patch("nanopub.fdo_ops.requests.get")
def test_create_fdo_nanopub_with_dataref(mock_get):
    mock_get.return_value = MagicMock(status_code=200, json=lambda: HANDLE_METADATA_WITH_DATAREF)

    fdonp = FdoNanopub.handle_to_nanopub(FDO_HANDLE)
    g = fdonp.assertion  
    fdo_uri = fdonp.fdo_uri
    profile_uri = to_hdl_uri(fdonp.fdo_profile)
    assert (profile_uri) == to_hdl_uri("21.T11966/996c38676da9ee56f8ab")
    dataref_uri = URIRef(HDL_PREFIX + DATAREF_HANDLE)

    assert (fdo_uri, FDOF.hasFdoProfile, profile_uri) in g
    assert (fdo_uri, FDOF.isMaterializedBy, dataref_uri) in g