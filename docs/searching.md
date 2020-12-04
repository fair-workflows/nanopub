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

## Interpreting search results
Each search method returns a list of dicts depicting matching nanopublications.

Each dict has the following key-value pairs:
* `date`: The date and time the nanopublication was created.
* `description`: A description of the nanopublication that was parsed from the nanopublication RDF.
* `np`: The URI of the matching nanopublication.

Example results (from `client.find_nanopubs_with_text('fair')`):
```python
[{'date': '2020-05-01T08:05:25.575Z',
  'description': 'The primary objective of the VODAN Implementation Network is '
                 'to showcase the creation and deployment of FAIR data related '
                 'to COVID-19',
  'np': 'http://purl.org/np/RAdDKjIGPt_2mE9oJtB3YQX6wGGdCC8ZWpkxEIoHsxOjE'},
 {'date': '2020-05-14T09:34:53.554Z',
  'description': 'FAIR IN community',
  'np': 'http://purl.org/np/RAPE0A-NrIZDeX3pvFJr0uHshocfXuUj8n_J3BkY0sMuU'}]
```

