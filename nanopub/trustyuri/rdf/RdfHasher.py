import hashlib
from nanopub.trustyuri import TrustyUriUtils
from nanopub.trustyuri.rdf.StatementComparator import StatementComparator
from rdflib.term import URIRef
import re
from functools import cmp_to_key
from nanopub.trustyuri.rdf.RdfPreprocessor import preprocess


def normalize_quads(quads, hashstr=None):
    quads = preprocess(quads, hashstr=hashstr)
    comp = StatementComparator(hashstr)
    quads = sorted(quads, key=cmp_to_key(lambda q1, q2: comp.compare(q1, q2)))
    s = ""
    previous = ""
    for q in quads:
        e = ""
        e = e + value_to_string(q[0])
        e = e + value_to_string(q[1])
        e = e + value_to_string(q[2])
        e = e + value_to_string(q[3])
        if not e == previous:
            s = s + e
        previous = e
    # log.debug("Normalized quads before signing/hashing:", s)
    return s


def make_hash(quads, hashstr=None):
    s = normalize_quads(quads, hashstr)

    # Uncomment next line to see what goes into the hash:
    #print "-----\n" + s + "-----\n"
    return "RA" + TrustyUriUtils.get_base64(hashlib.sha256(s.encode('utf-8')).digest())

def value_to_string(value):
    if value is None:
        return "\n"
    elif isinstance(value, URIRef):
        return value + "\n"
    else:
        if not value.language is None:
            # TODO: proper canonicalization of language tags
            return "@" + value.language.lower() + " " + escape(value) + "\n"
        if not value.datatype is None:
            return "^" + value.datatype + " " + escape(value) + "\n"
        return "^http://www.w3.org/2001/XMLSchema#string " + escape(value) + "\n"

def escape(s):
    return re.sub(r'\n', r'\\n', re.sub(r'\\', r'\\\\', s))
