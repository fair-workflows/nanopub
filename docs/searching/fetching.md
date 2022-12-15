# Fetching nanopublications
## Fetch from the default server

You can fetch nanopublications from the default nanopub server using the `Nanopub` class.

```python
from nanopub import Nanopub

# Fetch the nanopublication at the specified URI
np = Nanopub('http://purl.org/np/RApJG4fwj0szOMBMiYGmYvd5MCtRle6VbwkMJUb1SxxDM')

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

## Fetch from a specific server

You can fetch Nanopubs from the test server:

```python
from nanopub import Nanopub

np = Nanopub(
    source_uri='http://purl.org/np/RANGY8fx_EYVeZzJOinH9FoY-WrQBerKKUy2J9RCDWH6U',
	conf=NanopubConf(use_test_server=True)
)
print(np)
```

Or from a specific nanopub server:

```python
np = Nanopub(
    source_uri='http://purl.org/np/RApJG4fwj0szOMBMiYGmYvd5MCtRle6VbwkMJUb1SxxDM',
	conf=NanopubConf(use_server='https://np.petapico.org')
)
print(np)
```
