from rdflib import URIRef
from nanopub.namespaces import FDOF
from nanopub.fdo.fdo_nanopub import FdoNanopub
from nanopub.fdo.fdo_record import FdoRecord
from nanopub.fdo.retrieve import get_fdo_uri_from_fdo_record

def update_metadata(fdoNanopub: FdoNanopub, record: FdoRecord) -> URIRef:
    fdo_record = fdoNanopub.assertion
    subject_uri = get_fdo_uri_from_fdo_record(fdo_record)
    for p, o in list(fdo_record.predicate_objects(subject=subject_uri)):
        fdo_record.remove((subject_uri, p, o))
    for triple in record.get_statements():
        fdo_record.add(triple)
    fdoNanopub.update()
    return fdoNanopub.source_uri

def update_content(handle: str, content: bytes) -> None:
#    TODO: Not implemented yet
   raise NotImplementedError("Not implemented yet")

   