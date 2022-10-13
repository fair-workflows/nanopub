import logging

from rdflib import ConjunctiveGraph

from nanopub import Nanopub, NanopubClient, NanopubConfig, load_profile

log = logging.getLogger()
log.setLevel(logging.INFO)

config = NanopubConfig(
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=False,
    attribute_publication_to_profile=False,
    profile=load_profile(),
    use_test_server=True,
)

client = NanopubClient(
    use_test_server=True
    # profile_path='tests/resources'
)


# assertion = Graph()
# assertion.add((
#     URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
# ))


np_g = ConjunctiveGraph()
np_g.parse("./tests/testsuite/transform/signed/rsa-key1/simple1.in.trig", format="trig")


np = Nanopub(config=config, rdf=np_g)

# np = Nanopub(config=config, assertion=assertion)

np.sign()
# np.publish()

# np = client.sign(np)
# resp = client.publish(np)

print(np)


# if signed == True:
#     published = np.publish()
#     if published == True:
#         print(f"Published {np.source_uri}")
