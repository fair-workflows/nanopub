import re

from rdflib.term import URIRef, BNode
from nanopub.trustyuri.rdf import RdfUtils

def preprocess(quads, hashstr=None, baseuri=None, tmp_np_uri=None):
    newquads = []
    bnodemap = {}
    for q in quads:
        c = transform(q[0], hashstr, baseuri, bnodemap, tmp_np_uri)
        s = transform(q[1], hashstr, baseuri, bnodemap, tmp_np_uri)
        p = transform(q[2], hashstr, baseuri, bnodemap, tmp_np_uri)
        o = q[3]
        if isinstance(q[3], URIRef) or isinstance(q[3], BNode):
            o = transform(q[3], hashstr, baseuri, bnodemap, tmp_np_uri)
        newquads.append((c, s, p, o));
    return newquads

def transform(uri, hashstr, baseuri, bnodemap, tmp_np_uri=None):
    if uri is None: return None
    if tmp_np_uri is not None:
        # TODO: improve quick fix to replace temp nanopub URI by the placeholder
        suffix = ""
        if str(uri).lower().endswith("#sig"):
            suffix = "#"
        elif str(uri).lower().endswith("#pubinfo") or str(uri).lower().endswith("#head") or str(uri).lower().endswith("#assertion") or str(uri).lower().endswith("#provenance"):
            suffix = "#"
            # suffix = "#%23"

        try:
            # TODO: rdflib print disgusting warnings due to the space in the URIRef
            return URIRef(re.sub(tmp_np_uri, f"http://purl.org/np/ {suffix}", str(uri)))
        except:
            return URIRef(re.sub(tmp_np_uri.decode('utf-8'), " ", str(uri)))

    if baseuri is None:
        try:
            return URIRef(RdfUtils.normalize(uri, hashstr).decode('utf-8'))
        except:
            return URIRef(RdfUtils.normalize(uri, hashstr))
    return RdfUtils.get_trustyuri(uri, baseuri, " ", bnodemap)
