![Build Status](https://github.com/fair-workflows/nanopub/workflows/Python%20application/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/fair-workflows/nanopub/badge.svg?branch=main)](https://coveralls.io/github/fair-workflows/nanopub?branch=main)
[![PyPI version](https://badge.fury.io/py/nanopub.svg)](https://badge.fury.io/py/nanopub)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)


# nanopub
The ```nanopub``` library provides a high-level, user-friendly python interface for searching, publishing and retracting nanopublications.
Nanopublications are FAIR data containers for scientific results
and more, read more about them on http://nanopub.org/.

# Setup
Install using pip:
```
pip install nanopub
```

To publish to the nanopub server you need to setup your profile. This allows the nanopub server to identify you. Run 
the following interactive command:
```
setup_profile
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

# Search for nanopublications whose assertions contain triples that are ```rdf:Statement```s.
# Return only the first three results.
results = client.find_nanopubs_with_pattern(
                pred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                obj='http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement',
                max_num_results=3)
print(results)

# Search for nanopublications that introduce a concept that is a ```p-plan:Step```.
# Return only one result.
results = client.find_things('http://purl.org/net/p-plan#Step', max_num_results=1)
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

### Specifying concepts relative to the nanopublication namespace
You can optionally specify that the ```Publication``` introduces a particular concept using blank nodes. 
The pubinfo graph will note that this nanopub npx:introduces the concept. The concept should be a blank node 
(rdflib.term.BNode), and is converted to a URI derived from the nanopub's URI with a fragment (#) made from the blank
node's name.
```python
from rdflib.term import BNode
publication = Publication.from_assertion(assertion_rdf=my_assertion,
                                         introduces_concept=BNode('timbernerslee'))
```
Upon publication, any blank nodes in the rdf graph are replaced with the nanopub's URI, with the blank node name as a
fragment. For example, if the blank node is called 'step', that would result in a URI composed of the nanopub's (base)
URI, followed by #step. In case you are basing your publication on rdf that has a lot of concepts specific to this 
nanopublication that are not blank nodes you could use `replace_in_rdf` to easily replace them with blank nodes:
```python
from nanopub import replace_in_rdf
replace_in_rdf(rdf=my_assertion, oldvalue=URIRef('www.example.org/timbernerslee'), newvalue=BNode('timbernerslee'))
``` 

### Specifying derived_from
You can specify that the nanopub's assertion is derived from another URI (such as an existing nanopublication):
```python
publication = Publication.from_assertion(assertion_rdf=my_assertion,
                                         derived_from=rdflib.URIRef('www.example.org/another-nanopublication'))
```
Note that ```derived_from``` may also be passed a list of URIs.
                               
### Specifying custom publication info or provenance triples
You can add your own triples to the provenance graph of the nanopublication:
```python
from nanopub import namespaces
provenance_rdf = (BNode('timbernserslee'), namespaces.PROV.actedOnBehalfOf, BNode('markzuckerberg'))
publication = Publication.from_assertion(assertion_rdf=my_assertion,
                                         provenance_rdf=provenance_rdf)
```
and to the publication info graph of the nanopublication:
```python
from nanopub import namespaces
pubinfo_rdf = (BNode('activity'), RDF.type, namespaces.PROV.Activity)
publication = Publication.from_assertion(assertion_rdf=my_assertion,
                                         pubinfo_rdf=pubinfo_rdf)
```
                                         
## Dependencies
The ```nanopub``` library currently uses the [```nanopub-java```](https://github.com/Nanopublication/nanopub-java) tool for signing and publishing new nanopublications. This is automatically installed by the library.
