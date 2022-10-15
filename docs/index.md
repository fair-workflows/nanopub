
# Welcome to nanopub's documentation!

The `nanopub` library provides a high-level, user-friendly python interface for searching, publishing and retracting nanopublications.

Nanopublications are a formalized and machine-readable way of communicating the smallest possible units of publishable information. See the [What are Nanopublications?](getting-started/what-are-nanopubs) page for more information.

## Setup

Install using pip:

```bash
pip install nanopub
```

To publish to the nanopub server you need to setup your profile. This allows the nanopub server to identify you. To check if your profile is properly run the following command in your terminal:

```bash
np profile
```

To setup a profile run the following interactive command:

```bash
np setup
```

This will add and store RSA keys to sign your nanopublications, publish a nanopublication with your name and ORCID iD to declare that you are using using these RSA keys, and store your ORCID iD to automatically add as author to the provenance of any nanopublication you will publish using this library.

## Quick Start

### Publishing nanopublications

Use `load_profile()` to load the user profile from `$HOME/.nanopub`, and `use_test_server=True` to point to the test server (remove it to publish to the Nanopublication network)

```python
from rdflib import Graph
from nanopub import Nanopub, NanopubConf, load_profile

# 1. Create the config
np_conf = NanopubConf(
    use_test_server=True,
    profile=load_profile(),
    add_prov_generated_time=True,
    attribute_publication_to_profile=True,
)

# 2. Construct a desired assertion (a graph of RDF triples) using rdflib
my_assertion = Graph()
my_assertion.add((
    rdflib.URIRef('www.example.org/timbernerslee'),
    rdflib.RDF.type,
    rdflib.FOAF.Person
))

# 2. Make a Nanopub object with this assertion
np = Nanopub(
    config=np_conf,
    assertion=my_assertion
)

# 3. Publish the Nanopub object
np.publish()
print(np)
```

You can also just sign the nanopub with `np.sign()`. Upon signing, or publishing, the `np` object will be automatically updated with the signed RDF and generated trusty URI.

### Searching for nanopublications

```python
from nanopub import NanopubClient

# Create the client
client = NanopubClient()

# Search for all nanopublications containing the text 'fair'
results = client.find_nanopubs_with_text('fair')
for result in results:
	print(result)
```

### Fetching nanopublications and inspecting them

```python
from nanopub import NanopubClient

# Create the client
client = NanopubClient()

# Fetch the nanopublication at the specified URI
np = client.fetch('http://purl.org/np/RApJG4fwj0szOMBMiYGmYvd5MCtRle6VbwkMJUb1SxxDM')
print(np)

# Iterate through all triples in the assertion graph
for s, p, o in np.assertion:
	print(s, p, o)
```
