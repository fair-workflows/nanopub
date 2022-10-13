import logging

from rdflib import Graph, Literal, URIRef

from nanopub import Nanopub, NanopubClient, NanopubConfig, load_profile, namespaces

log = logging.getLogger()
log.setLevel(logging.INFO)

assertion = Graph()
# assertion.add(( URIRef("http://s"), URIRef("http://p"), URIRef("http://o")))
assertion.add((
    URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
))

config = NanopubConfig(
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=True,
    attribute_publication_to_profile=True,
    profile=load_profile(),
    use_test_server=True,
)

client = NanopubClient(
    use_test_server=True
    # profile_path='tests/resources'
)

np = Nanopub(config=config, assertion=assertion)

np.sign()
# np.publish()

# np = client.sign(np)

# resp = client.publish(np)

print(np)
# print(resp)



# np = client.create_nanopub(
#     assertion=assertion,
#     # provenance=prov,
#     # pubinfo=pubinfo,
#     nanopub_config=config,
# )
# np = client.sign(np)
# resp = client.publish(np)
# print(np)
# print(resp)







## NEW WORKFLOW:

# assertion = Graph()
# # assertion.add(( URIRef("http://s"), URIRef("http://p"), URIRef("http://o")))
# assertion.add((
#     URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
# ))


# client = NanopubClient(
#     use_test_server=True,

#     add_prov_generated_time=False,
#     add_pubinfo_generated_time=False,
#     attribute_assertion_to_profile=True,
#     attribute_publication_to_profile=True,
# )

# np = Nanopub(client=client, assertion=assertion)


# signed = np.sign()

# if signed == True:
#     published = np.publish()
#     if published == True:
#         print(f"Published {np.source_uri}")
