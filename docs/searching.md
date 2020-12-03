# Searching the nanopub server
The `NanopubClient` provides methods for searching the nanopub server. It provides
an (uncomplete) mapping to the [nanopub server grlc endpoint](http://grlc.nanopubs.lod.labs.vu.nl/api/local/local).

## Text search
Search for all nanopublications containing some text using 
`NanopubClient.find_nanopubs_with_text()`
```python
from nanopub import NanopubClient
client = NanopubClient()
results = client.find_nanopubs_with_text('fair', max_num_results=3)
```

## Triple pattern search
Search for nanopublications whose assertions contain triples that match a specific pattern.
```python
from nanopub import NanopubClient
client = NanopubClient()
# Search for nanopublications whose assertions contain triples that are ```rdf:Statement```s.
results = client.find_nanopubs_with_pattern(
                pred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                obj='http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement',
                max_num_results=3)
```

## Search on introduced concept
Search for any nanopublications that introduce a concept of the given type, that contain 
text with the given search term.
```python
from nanopub import NanopubClient
client = NanopubClient()
# Search for nanopublications that introduce a concept that is a ```p-plan:Step```.
results = client.find_things('http://purl.org/net/p-plan#Step', max_num_results=1)
```
