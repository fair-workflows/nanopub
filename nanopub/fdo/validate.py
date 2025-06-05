import json
import requests
from pyshacl import validate
from nanopub.fdo.utils import convert_jsonschema_to_shacl


def validate_fdo_nanopub(fdo_nanopub) -> bool:
    try:
        profile_uri = f"https://hdl.handle.net/api/handles/{fdo_nanopub.fdo_profile}"
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

        schema_response = requests.get(jsonschema_url)
        json_schema = schema_response.json()
        shape_graph = convert_jsonschema_to_shacl(json_schema)

        conforms, _, results_text = validate(
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

        return conforms

    except Exception as e:
        print("Validation error:", e)
        return False
