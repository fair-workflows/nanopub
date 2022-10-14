import re

from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.term import BNode, URIRef
from rdflib.util import guess_format

from nanopub.definitions import FINAL_NANOPUB_URI, NP_TEMP_PREFIX


def get_trustyuri(resource, baseuri, hashstr, bnodemap):
    if resource is None:
        return None
    prefix = baseuri
    if str(baseuri).startswith(NP_TEMP_PREFIX):
        prefix = FINAL_NANOPUB_URI
    if isinstance(resource, URIRef):
        suffix = get_suffix(resource, baseuri)
        if suffix is None and not get_str(resource) == get_str(baseuri):
            return resource
        if suffix is None or suffix == "":
            return str(f"{prefix}{hashstr}")
        if hashstr == " " and suffix.startswith("_"):
            # Add a _ to suffix of URIs starting with a _ to
            # not confond with blanknodes which are starting with a _
            suffix = f"_{suffix}"
        return str(f"{prefix}{hashstr}#{suffix}")
    if isinstance(resource, BNode):
        n = get_bnode_number(resource, bnodemap)
        np_uri = str(f"{prefix}{hashstr}")
        return str(np_uri + "#_" + str(n))
    else:
        return None


def get_suffix(plainuri, baseuri):
    p = get_str(plainuri)
    b = get_str(baseuri)
    if (p == b):
        return None
    if (p.startswith(b)):
        return p[len(b):].decode('utf-8')
    return None


def normalize(uri, hashstr):
    if hashstr is None:
        return get_str(uri)
    try:
        return re.sub(hashstr, " ", str(uri))
    except Exception:
        return re.sub(hashstr.decode('utf-8'), " ", str(uri))


def get_bnode_number(bnode, bnodemap):
    i = get_str(bnode)
    if i not in bnodemap.keys():
        n = len(bnodemap) + 1
        bnodemap[i] = n
    return bnodemap[i]


def expand_baseuri(baseuri):
    s = get_str(baseuri).decode('utf-8')
    if re.match(r'.*[A-Za-z0-9\-_]', s):
        s = s + "."
    return s


def get_quads(conjunctivegraph):
    quads = []
    for s, p, o, c in conjunctivegraph.quads((None, None, None)):
        g = c.identifier
        if not isinstance(g, URIRef):
            g = None
        quads.append((g, s, p, o))
    quads.sort()
    return quads


def get_conjunctivegraph(quads):
    cg = ConjunctiveGraph()
#     for (c, s, p, o) in quads:
#         cg.default_context = Graph(store=cg.store, identifier=c)
#         cg.add((s, p, o))
    cg.addN([(s, p, o, Graph(store=cg.store, identifier=c)) for (c, s, p, o) in quads])
    return cg


def get_format(filename):
    return guess_format(filename, {'xml': 'trix', 'ttl': 'turtle', 'nq': 'nquads', 'nt': 'nt', 'rdf': 'xml'})


def get_str(s):
    return s.encode('utf-8')


# def get_trustyuri_str(baseuri, hashstr, suffix=None):
#     # s = expand_baseuri(baseuri) + hashstr
#     # try:
#     #     # TODO: fix the horrible rdflib warnings due to the space in the URIRef
#     #     return URIRef(re.sub(baseuri, f"http://purl.org/np/ {suffix}", str(resource)))
#     # except:
#     #     return URIRef(re.sub(baseuri.decode('utf-8'), " ", str(uri)))
#     if suffix is not None:
#         suffix = suffix.decode('utf-8')
#         if suffix.startswith("_"):
#             # Make two underscores, as one underscore is reserved for blank nodes
#             s = s + "#_" + suffix
#         else:
#             s = s + "#" + suffix
#     return s
