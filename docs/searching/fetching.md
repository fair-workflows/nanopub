# Fetching nanopublications
You can fetch nanopublications from the nanopub server using `NanopubClient.fetch()`. The resulting object is a `Nanopub` object that you can use to inspect the nanopublication.
```python
from nanopub import NanopubClient

# Fetch the nanopublication at the specified URI
client = NanopubClient()
publication = client.fetch('http://purl.org/np/RApJG4fwj0szOMBMiYGmYvd5MCtRle6VbwkMJUb1SxxDM')

# Print the RDF contents of the nanopublication
print(publication)

# Iterate through all triples in the assertion graph
for s, p, o in publication.assertion:
    print(s, p, o)

# Iterate through the publication info
for s, p, o in publication.pubinfo:
    print(s, p, o)

# Iterate through the provenance graph
for s, p, o in publication.provenance:
    print(s,p,o)

# See the concept that is introduced by this nanopublication (if any)
print(publication.introduces_concept)
```
