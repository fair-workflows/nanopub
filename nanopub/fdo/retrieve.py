import requests
from nanopub.fdo.utils import looks_like_handle
from nanopub.fdo.fdo_record import FdoRecord
from nanopub.fdo import FdoNanopub
from rdflib import RDF
from nanopub.namespaces import FDOF


def retrieve_metadata_from_id(iri_or_handle: str):
    if looks_like_handle(iri_or_handle):
        np = FdoNanopub.handle_to_nanopub(iri_or_handle)
        return FdoRecord(np.assertion)
    else:
        raise NotImplementedError("Non-handle IRIs not yet supported")


def retrieve_content_from_id(iri_or_handle: str):
    raise NotImplementedError("Not implemented yet")


def resolve_handle_metadata(handle: str) -> dict:
    url = f"https://hdl.handle.net/api/handles/{handle}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_fdo_uri_from_fdo_record(fdo_record):
    fdo_uris = list(fdo_record.subjects(RDF.type, FDOF.FAIRDigitalObject))
    if not fdo_uris:
        raise ValueError("No FAIRDigitalObject found in assertion.")
    if len(fdo_uris) > 1:
        raise ValueError("Multiple FAIRDigitalObjects found; cannot disambiguate.")
    return fdo_uris[0]