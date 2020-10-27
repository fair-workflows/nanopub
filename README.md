![Build Status](https://github.com/fair-workflows/nanopub/workflows/Python%20application/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/fair-workflows/nanopub/badge.svg?branch=main)](https://coveralls.io/github/fair-workflows/nanopub?branch=main)
[![PyPI version](https://badge.fury.io/py/nanopub.svg)](https://badge.fury.io/py/nanopub)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)


# nanopub
The ```nanopub``` library provides a high-level, user-friendly python interface for searching, publishing and modifying nanopublications.

# Setup
Install using pip:
```
pip install nanopub
```

To publish to the nanopub server you need to setup RSA keys. This allows the nanopub server to identify you.
```
make_nanopub_keys
```

## Quick Start

### Searching for nanopublications
```python
from nanopub import NanopubClient

# Create the client, that allows searching, fetching and publishing nanopubs
client = NanopubClient()

# Search for all nanopublications containing the text 'fair'
results = client.search_text('fair')
print(results)

# Search for nanopublications whose assertions contain triples that are ```rdf:Statement```s.
# Return only the first three results.
results = client.search_pattern(
                pred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                obj='http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement',
                max_num_results=3)
print(results)

# Search for nanopublications that introduce a concept that is a ```p-plan:Step```.
# Return only one result.
results = client.search_things('http://purl.org/net/p-plan#Step', max_num_results=1)
print(results)
```

### Fetching nanopublications and inspecting them
```python
# Fetch the nanopublication at the specified URI
np = client.fetch('http://purl.org/np/RApJG4fwj0szOMBMiYGmYvd5MCtRle6VbwkMJUb1SxxDM')

# Print the RDF contents of the nanopublication
print(np)

# Iterate through all triples in the assertion graph
for s, p, o in np.assertion:
    print(s, p, o)

# Iterate through the publication info
for s, p, o in np.pubinfo:
    print(s, p, o)

# Iterate through the provenance graph
for s, p, o in np.provenance:
    print(s,p,o)

# See the concept that is introduced by this nanopublication (if any)
print(np.introduces_concept)
```

### Publishing an assertion as a nanopub
```python

from nanopub import Nanopub, NanopubClient
from rdflib import Graph, URIRef, RDF, FOAF

# Construct your desired assertion (a graph of RDF triples)
my_assertion = Graph()
my_assertion.add( (URIRef('www.example.org/timbernerslee'), RDF.type, FOAF.Person) )

# Make a Nanopub object with this assertion
nanopub = Nanopub.from_assertion(assertion_rdf=my_assertion)

# Publish the Nanopub object. The URI at which it is published is returned.
publication_info = client.publish(nanopub)
print(publication_info['nanopub_uri']) # The URI at which it is published
```

### Specifying more information
You can optionally specify that the ```Nanopub``` introduces a particular concept, or is derived from another nanopublication:
```python
nanopub = Nanopub.from_assertion(   assertion_rdf=my_assertion,
                                    introduces_concept=(URIRef('www.example.org/timbernerslee'),
                                    derived_from=URIRef('www.example.org/another-nanopublication') )
```

## Dependencies
The ```nanopub``` library currently uses the [```nanopub-java```](https://github.com/Nanopublication/nanopub-java) tool for signing and publishing new nanopublications. This is automatically installed by the library.
