![Build Status](https://github.com/fair-workflows/nanopub/workflows/Python%20application/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/nanopub/badge/?version=latest)](https://nanopub.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/fair-workflows/nanopub/badge.svg?branch=main)](https://coveralls.io/github/fair-workflows/nanopub?branch=main)
[![PyPI version](https://badge.fury.io/py/nanopub.svg)](https://badge.fury.io/py/nanopub)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4491/badge)](https://bestpractices.coreinfrastructure.org/projects/4491)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F-green)](https://fair-software.eu)
[![DOI](https://zenodo.org/badge/302247101.svg)](https://zenodo.org/badge/latestdoi/302247101)

# nanopub
The ```nanopub``` library provides a high-level, user-friendly python interface for searching, publishing and retracting nanopublications.

Nanopublications are a formalized and machine-readable way of communicating
the smallest possible units of publishable information. See [the documentation](https://nanopub.readthedocs.io/en/latest/getting-started/what-are-nanopubs.html)
for more information.

# Documentation

Checkout the [user documentation](https://nanopub.readthedocs.io/)

# Setup
Install using pip:
```
pip install nanopub
```

To publish to the nanopub server you need to setup your profile. This allows the nanopub server to identify you. Run 
the following interactive command:
```
setup_nanopub_profile
```
It will add and store RSA keys to sign your nanopublications, publish a nanopublication with your name and ORCID iD to
declare that you are using using these RSA keys, and store your ORCID iD to automatically add as author to the
provenance of any nanopublication you will publish using this library.

## Quick Start


### Publishing nanopublications
```python

from nanopub import Publication, NanopubClient
from rdflib import Graph, URIRef, RDF, FOAF

# Create the client, that allows searching, fetching and publishing nanopubs
client = NanopubClient()

# Either quickly publish a statement to the server
client.claim('All cats are gray')

# Or: 1. construct a desired assertion (a graph of RDF triples)
my_assertion = Graph()
my_assertion.add( (URIRef('www.example.org/timbernerslee'), RDF.type, FOAF.Person) )

# 2. Make a Publication object with this assertion
publication = Publication.from_assertion(assertion_rdf=my_assertion)

# 3. Publish the Publication object. The URI at which it is published is returned.
publication_info = client.publish(publication)
print(publication_info)
```


### Searching for nanopublications
```python
from nanopub import NanopubClient

# Search for all nanopublications containing the text 'fair'
results = client.find_nanopubs_with_text('fair')
print(results)
```

### Fetching nanopublications and inspecting them
```python
# Fetch the nanopublication at the specified URI
publication = client.fetch('http://purl.org/np/RApJG4fwj0szOMBMiYGmYvd5MCtRle6VbwkMJUb1SxxDM')

# Print the RDF contents of the nanopublication
print(publication)

# Iterate through all triples in the assertion graph
for s, p, o in publication.assertion:
    print(s, p, o)

```
                                         
## Dependencies
The ```nanopub``` library currently uses the [```nanopub-java```](https://github.com/Nanopublication/nanopub-java) tool for signing and publishing new nanopublications. This is automatically installed by the library.
