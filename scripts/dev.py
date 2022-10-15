import logging

from rdflib import Graph, Literal, URIRef

from nanopub import Nanopub, NanopubConf, load_profile, namespaces

log = logging.getLogger()
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: [%(module)s:%(funcName)s] %(message)s"
)
console_handler.setFormatter(formatter)
log.addHandler(console_handler)


config = NanopubConf(
    add_prov_generated_time=False,
    add_pubinfo_generated_time=True,
    attribute_assertion_to_profile=True,
    attribute_publication_to_profile=True,
    profile=load_profile(),
    # use_test_server=True,
)

assertion = Graph()
assertion.add((
    URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test for the nanopub python library')
))


# np_g = ConjunctiveGraph()
# np_g.parse("./tests/testsuite/transform/signed/rsa-key1/simple1.in.trig", format="trig")


np = Nanopub(conf=config, assertion=assertion)

# np = Nanopub(config=config, assertion=assertion)

# np.sign()
np.publish()
# 1. Published at http://app.tkuhn.eculture.labs.vu.nl/nanopub-server-1/RABsDnLcLfgVcVSL9Tog2DJWHRphJjL9X0hEP3_FM4tEs
# But not properly redirected from https://purl.org/np/RABsDnLcLfgVcVSL9Tog2DJWHRphJjL9X0hEP3_FM4tEs

# 2. Also at http://app.tkuhn.eculture.labs.vu.nl/nanopub-server-1/RAFlANSXJPlQb0GVIgGtwLR1x8cYvjSsCCldJTLE4M7UE
# https://purl.org/np/RAFlANSXJPlQb0GVIgGtwLR1x8cYvjSsCCldJTLE4M7UE

# 3. Published to official server
# http://purl.org/np/RAHHhvsxFgr_SxeLjALNwygeuoJaOOtW7VOhm-e4wRJA0

# np = client.sign(np)
# resp = client.publish(np)

print(np)


# if signed == True:
#     published = np.publish()
#     if published == True:
#         print(f"Published {np.source_uri}")
