from rdflib import Graph, URIRef, Literal

from nanopub import NanopubClient, NanopubConfig, namespaces

assertion = Graph()
# assertion.add(( URIRef("http://s"), URIRef("http://p"), URIRef("http://o")))
assertion.add((
    URIRef('http://test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
))

client = NanopubClient(
    # profile_path='tests/resources'
)

np = client.create_nanopub(
    assertion=assertion,
    # provenance=prov,
    # pubinfo=pubinfo,
    nanopub_config=NanopubConfig(
        add_prov_generated_time=False,
        add_pubinfo_generated_time=False,
        attribute_assertion_to_profile=True,
        attribute_publication_to_profile=True,
    ),
)

np = client.sign(np)

print(np)