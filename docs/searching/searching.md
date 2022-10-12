# Searching the nanopub server
The `NanopubClient` provides methods for searching the nanopub server. It provides an (uncomplete) mapping to the [nanopub server grlc endpoint](http://grlc.nanopubs.lod.labs.vu.nl/api/local/local).

## Text search
Search for all nanopublications containing some text using `NanopubClient.find_nanopubs_with_text()`
```python
from nanopub import NanopubClient
client = NanopubClient()
results = client.find_nanopubs_with_text('fair')
```

## Triple pattern search
Search for nanopublications whose assertions contain triples that match a specific pattern.
```python
from nanopub import NanopubClient
client = NanopubClient()
# Search for nanopublications whose assertions contain triples that are ```rdf:Statement```s.
results = client.find_nanopubs_with_pattern(
    pred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
    obj='http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement'
)
```

## Search on introduced concept
Search for any nanopublications that introduce a concept of the given type, that contain text with the given search term.
```python
from nanopub import NanopubClient
client = NanopubClient()
# Search for nanopublications that introduce a concept that is a ```p-plan:Step```.
results = client.find_things('http://purl.org/net/p-plan#Step')
```

## Interpreting search results
Each search method returns a generator of dicts depicting matching nanopublications.

Each dict has the following key-value pairs:
* `date`: The date and time the nanopublication was created.
* `description`: A description of the nanopublication that was parsed from the nanopublication RDF.
* `np`: The URI of the matching nanopublication.

Example results (from `NanopubClient.find_nanopubs_with_text('fair')`):
```python
print(list(results))
[{'date': '2020-05-01T08:05:25.575Z',
  'description': 'The primary objective of the VODAN Implementation Network is '
                 'to showcase the creation and deployment of FAIR data related '
                 'to COVID-19',
  'np': 'http://purl.org/np/RAdDKjIGPt_2mE9oJtB3YQX6wGGdCC8ZWpkxEIoHsxOjE'},
 {'date': '2020-05-14T09:34:53.554Z',
  'description': 'FAIR IN community',
  'np': 'http://purl.org/np/RAPE0A-NrIZDeX3pvFJr0uHshocfXuUj8n_J3BkY0sMuU'}]
```

## Returning retracted publications in search
By default nanopublications that have a valid retraction do not show up in search results. A valid retraction is a retraction that is signed with the same public key as the nanopublication that it retracts.

You can toggle this behavior with the `filter_retracted` parameter, here is an example with `NanopubClient.find_nanopubs_with_text`:

```python
from nanopub import NanopubClient
client = NanopubClient()
# Search for nanopublications containing the text fair, also returning retracted publications.
results = client.find_nanopubs_with_text('fair', filter_retracted=False)
```

## Filtering search results for a particular publication key
You can filter search results to publications that are signed with a specific publication key (effectively filtering on publications from a single author). 

You use the `pubkey` argument for that. Here is an example with `NanopubClient.find_nanopubs_with_text`:

```python
from nanopub import NanopubClient, profile
# Search for nanopublications containing the text 'test',
# filtering on publications signed with my publication key.
client = NanopubClient(use_test_server=True)
my_public_key = profile.get_public_key()
results = client.find_nanopubs_with_text('test', pubkey=my_public_key)
```
