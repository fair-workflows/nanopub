from rdflib.term import URIRef
import re

def addhash(quads, hashstr):
    newquads = []
    for q in quads:
        c = transform(q[0], hashstr)
        s = transform(q[1], hashstr)
        p = transform(q[2], hashstr)
        o = q[3]
        if isinstance(q[3], URIRef):
            o = transform(q[3], hashstr)
        newquads.append((c, s, p, o));
    return newquads

def transform(uri, hashstr):
    if uri is None: return None
    return URIRef(re.sub(" ", hashstr, str(uri)))
