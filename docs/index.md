
# Welcome to nanopub's documentation!

The `nanopub` library provides a high-level, user-friendly python interface for searching, publishing and retracting nanopublications.

Nanopublications are a formalized and machine-readable way of communicating the smallest possible units of publishable information. See [doc](getting-started/what-are-nanopubs) for more information.

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

```python
from rdflib import Graph
from nanopub import Nanopub, NanopubConfig, load_profile

# Create the config (we use use_test_server=True to point to the test server)
np_config = NanopubConfig(
    profile=load_profile(),
    use_test_server=True,
    add_prov_generated_time=True,
    attribute_publication_to_profile=True,
)

# 1. construct a desired assertion (a graph of RDF triples) using rdflib
my_assertion = Graph()
my_assertion.add((
    rdflib.URIRef('www.example.org/timbernerslee'),
    rdflib.RDF.type,
    rdflib.FOAF.Person
))

# 2. Make a Nanopublication object with this assertion
np = Nanopub(
    config=np_config,
    assertion=my_assertion
)

# 3. Publish the Publication object.
np.publish()
print(np)
```

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
publication = client.fetch('http://purl.org/np/RApJG4fwj0szOMBMiYGmYvd5MCtRle6VbwkMJUb1SxxDM')

# Print the RDF contents of the nanopublication
print(publication)

# Iterate through all triples in the assertion graph
for s, p, o in publication.assertion:
print(s, p, o)
```
