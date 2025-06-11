import json
import requests
from pyshacl import validate
from rdflib import Graph
from nanopub.fdo.utils import convert_jsonschema_to_shacl
from nanopub.fdo.fdo_record import FdoRecord 


def validate_fdo_record(record: FdoRecord) -> bool:
    try:
        profile_uri = record.get_profile()
        if not profile_uri:
            print("FDO profile URI not found in record.")
            return False

        handle = str(profile_uri).split("/")[-1]
        profile_api_url = f"https://hdl.handle.net/api/handles/{handle}"
        profile_response = requests.get(profile_api_url)
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

        schema_response = requests.get(jsonschema_url)
        json_schema = schema_response.json()
        shape_graph = convert_jsonschema_to_shacl(json_schema)

        graph = record.get_graph()

        conforms, _, results_text = validate(
            graph,
            shacl_graph=shape_graph,
            inference='rdfs',
            abort_on_first=False,
            meta_shacl=False,
            advanced=True,
            debug=False
        )

        if not conforms:
            print("Validation failed:\n", results_text)

        return conforms

    except Exception as e:
        print("Validation error:", e)
        return False
