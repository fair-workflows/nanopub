import sys, logging
from rdflib.graph import ConjunctiveGraph
from nanopub.trustyuri.rdf import RdfUtils, RdfTransformer
from rdflib.term import URIRef
import os

def transform(args):
    filename = args[0]
    baseuristr = args[1]

    with open(filename, "r") as f:
        rdfFormat = RdfUtils.get_format(filename)
        cg = ConjunctiveGraph()
        cg.parse(data=f.read(), format=rdfFormat)
        baseuri = URIRef(baseuristr)
        outdir = os.path.abspath(os.path.join(str(filename), os.pardir))
        RdfTransformer.transform_to_file(cg, baseuri, outdir, filename)

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    args = sys.argv
    args.pop(0)
    transform(args)
