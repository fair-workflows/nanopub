import json
import rdflib
import requests
from pyshacl import validate
from rdflib import RDF, URIRef, Literal, Namespace
from rdflib.namespace import SH, XSD
from nanopub.constants import FDO_PROFILE_HANDLE
from nanopub.fdo_nanopub import FDONanopub
from nanopub.fdo_metadata import FdoMetadata

def looks_like_handle(value: str) -> bool:
    return isinstance(value, str) and not value.startswith("http")

def _convert_jsonschema_to_shacl(json_schema: dict) -> rdflib.Graph:
    EX = Namespace("https://example.org/shapes")
    HDL = Namespace("https://hdl.handle.net/")

    g = rdflib.Graph()
    g.bind("sh", SH)
    g.bind("xsd", XSD)
    g.bind("ex", EX)
    g.bind("hdl", HDL)

    node_shape = EX["FdoProfileShape"]
    g.add((node_shape, RDF.type, SH.NodeShape))
    # TODO: targetClass might be something else
    g.add((node_shape, SH.targetClass, URIRef("https://w3id.org/fdof/ontology#FairDigitalObject")))  
    g.add((node_shape, SH.closed, Literal(False)))

    for field in json_schema.get("required", []):
        prop_shape = EX[field.replace("/", "_")]
        g.add((node_shape, SH.property, prop_shape))
        g.add((prop_shape, RDF.type, SH.PropertyShape))
        g.add((prop_shape, SH.path, URIRef(f"https://hdl.handle.net/{field}")))
        g.add((prop_shape, SH.minCount, Literal(1)))
        g.add((prop_shape, SH.maxCount, Literal(1)))
        g.add((prop_shape, SH.datatype, XSD.string))

    return g

def retrieve_metadata_from_id(iri_or_handle: str):
    if looks_like_handle(iri_or_handle):
        np = create_fdo_nanopub_from_handle(iri_or_handle)
        return FdoMetadata(np.assertion)
    else:
        raise NotImplementedError("Non-handle IRIs not yet supported")

def retrieve_content_from_id(iri_or_handle: str):
    # TODO Not Implemented Yet
    raise NotImplementedError("Not implemented yet")

def validate_fdo_nanopub(fdo_nanopub) -> bool:
    """
    Validate an FDONanopub instance against its FDO profile's JSON Schema converted to SHACL.
    Returns True if valid, False otherwise.
    """
    try:
        profile_uri = "https://hdl.handle.net/api/handles/" + fdo_nanopub.fdo_profile
        profile_response = requests.get(profile_uri)
        profile_data = profile_response.json()

        jsonschema_entry = next(
            (v for v in profile_data.get("values", []) if v.get("type") == "21.T11966/JsonSchema"),
            None
        )

        if not jsonschema_entry:
            print("JSON Schema entry not found in FDO profile.")
            return False

        raw_value = jsonschema_entry["data"]["value"]
        parsed_value = json.loads(raw_value)
        jsonschema_url = parsed_value.get("$ref")

        if not jsonschema_url:
            print("JSON Schema $ref not found.")
            return False

        # Fetch the actual JSON schema
        schema_response = requests.get(jsonschema_url)
        json_schema = schema_response.json()

        # Convert JSON schema to SHACL
        shape_graph = _convert_jsonschema_to_shacl(json_schema)

        # Validate the assertion graph
        conforms, results_graph, results_text = validate(
            fdo_nanopub.assertion, 
            shacl_graph=shape_graph,
            inference='rdfs',
            abort_on_first=False,
            meta_shacl=False,
            advanced=True,
            debug=False
        )

        if not conforms:
            print("Validation failed:\n", results_text)

        # TODO: conforms will be true if no matches are found, need a way to check for matches
        return conforms

    except Exception as e:
        print("Validation error:", e)
        return False

def resolve_handle_metadata(handle: str) -> dict:
    url = f"https://hdl.handle.net/api/handles/{handle}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def create_fdo_nanopub_from_handle(handle: str, **kwargs) -> FDONanopub:
    data = resolve_handle_metadata(handle)
    values = data.get("values", [])

    label = None
    profile = None
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
        else:
            other_attributes.append((entry_type, entry_value))

    if not profile:
        raise ValueError("FDO profile missing in handle metadata")
    fdo_profile = profile
    fdonp = FDONanopub(fdo_id=handle, label=label or "", fdo_profile=fdo_profile, **kwargs)
    fdonp.add_fdo_profile(rdflib.URIRef(fdo_profile))

    for attr_type, attr_value in other_attributes:
        attr_uri = rdflib.URIRef(f"https://w3id.org/kpxl/handle/terms/{attr_type}")
        fdonp.add_attribute(attr_uri, rdflib.Literal(attr_value))
        fdonp.add_attribute_label(attr_uri, attr_type)

    return fdonp

def update_metadata(handle: str, metadata: FdoMetadata) -> None:
#    TODO: Not implemented yet
   raise NotImplementedError("Not implemented yet")


def update_content(handle: str, content: bytes) -> None:
#    TODO: Not implemented yet
   raise NotImplementedError("Not implemented yet")

   