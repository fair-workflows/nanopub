import requests
from nanopub import NanopubClient, Nanopub
from nanopub.fdo.utils import looks_like_handle
from nanopub.fdo.fdo_record import FdoRecord
from nanopub.fdo import FdoNanopub
from rdflib import RDF, URIRef
from nanopub.namespaces import FDOF, FDOC

def resolve_id(iri_or_handle: str) -> FdoRecord:
    try:
        np = resolve_in_nanopub_network(iri_or_handle)
        if np is not None:
            return FdoRecord(np.assertion)

        if looks_like_handle(iri_or_handle):
            np = FdoNanopub.handle_to_nanopub(iri_or_handle)
            return FdoRecord(np.assertion)

        from rdflib import URIRef
        if iri_or_handle.startswith("https://hdl.handle.net/"):
            handle = iri_or_handle.replace("https://hdl.handle.net/", "")
            np = FdoNanopub.handle_to_nanopub(handle)
            return FdoRecord(np.assertion)

    except Exception as e:
        raise ValueError(f"Could not resolve FDO: {iri_or_handle}") from e

    raise ValueError(f"FDO not found: {iri_or_handle}")

def resolve_in_nanopub_network(fdo_id: str):
    query_id = "RAs0HI_KRAds4w_OOEMl-_ed0nZHFWdfePPXsDHf4kQkU"
    endpoint = "get-fdo-by-id"
    query_url = f"https://query.knowledgepixels.com/api/{query_id}/"

    data = NanopubClient()._query_api_parsed(
        params={"fdoid": fdo_id},
        endpoint=endpoint,
        query_url=query_url,
    )

    if not data:
        return None
    np_uri = data[0].get("np")
    if not np_uri:
        return None

    return Nanopub(np_uri)


def retrieve_record_from_id(iri_or_handle: str):
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

def get_fdo_uri_from_fdo_record(fdo_record: FdoRecord) -> URIRef:
    if not fdo_record.id:
        raise ValueError("FDO Record has no ID")
    return URIRef(f"https://hdl.handle.net/{fdo_record.id}")