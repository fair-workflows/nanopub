# Retracting a nanopublication
A nanopublication is persistent, you can never edit nor delete it.
You can however retract a nanopublication.
This is done by publishing a new nanopublication that states that you
retract the original publication. You can use `NanopubClient.retract()`:
```python
>>> from nanopub import NanopubClient
>>> client = NanopubClient(use_test_server=True)
>>> client.retract('http://purl.org/np/RAfk_zBYDerxd6ipfv8fAcQHEzgZcVylMTEkiLlMzsgwQ')
Published to http://purl.org/np/RAv75Xhhz5jv--Nnu9RDqIGy2xHr74REGC4vtOSxrwX4c
```
View the full retraction nanopublication [here](http://purl.org/np/RAv75Xhhz5jv--Nnu9RDqIGy2xHr74REGC4vtOSxrwX4c).

The assertion states that the researcher (denoted by the ORCID iD from your profile)
retracts the provided nanopublication:
```
@prefix npx: <http://purl.org/nanopub/x/> .
@prefix sub: <http://purl.org/np/RAv75Xhhz5jv--Nnu9RDqIGy2xHr74REGC4vtOSxrwX4c#> .

sub:assertion {
    <https://orcid.org/0000-0000-0000-0000> npx:retracts <http://purl.org/np/RAfk_zBYDerxd6ipfv8fAcQHEzgZcVylMTEkiLlMzsgwQ> .
}
```
By default nanopublications that have a valid retraction do not show up in search results.
A valid retraction is a retraction that is signed with the same public key as 
the nanopublication that it retracts.

## Retracting a nanopublication that is not yours
By default we do not retract nanopublications that are not yours (i.e. signed with another public key). 
If you try to do this it will trigger an AssertionError:
```python
>>> from nanopub import NanopubClient
>>> client = NanopubClient(use_test_server=True)
>>> not_my_nanopub_uri = 'http://purl.org/np/RAr6rs7o8Sr5OGCs0127ah37DYUvgiWzjOuCvV-OSusAk'
>>> client.retract(not_my_nanopub_uri)
---------------------------------------------------------------------------
AssertionError                            Traceback (most recent call last)
<ipython-input-30-7141d9e82fbc> in <module>
      1 not_my_nanopub_uri = 'http://purl.org/np/RAr6rs7o8Sr5OGCs0127ah37DYUvgiWzjOuCvV-OSusAk'
----> 2 client.retract(not_my_nanopub_uri)

~/projects/fair-workflows/nanopub/nanopub/client.py in retract(self, uri, force)
    265         """
    266         if not force:
--> 267             self._check_public_keys_match(uri)
    268         assertion_rdf = rdflib.Graph()
    269         orcid_id = profile.get_orcid_id()

~/projects/fair-workflows/nanopub/nanopub/client.py in _check_public_keys_match(self, uri)
    245                               f'this one: {their_public_key}')
    246             if their_public_key != profile.get_public_key():
--> 247                 raise AssertionError('The public key in your profile does not match the public key'
    248                                      'that the publication that you want to retract is signed '
    249                                      'with. Use force=True to force retraction anyway.')

AssertionError: The public key in your profile does not match the public keythat the publication that you want to retract is signed with. Use force=True to force retraction anyway.
```
We can use force=True to override this behavior:
```python
client.retract(not_my_nanopub_uri, force=True)
```

## Find retractions of a given nanopublication
You can find out whether a given publication is retracted 
and what the nanopublications are that retract it using `NanopubClient.find_retractions_of`:
```python
>>> from nanopub import NanopubClient
>>> client = NanopubClient(use_test_server=True)
>>> # This URI has 1 retraction:
>>> client.find_retractions_of('http://purl.org/np/RAirauh-vy5f7UJEMTm08C5bh5pnWD-abb-qk3fPYWCzc')
['http://purl.org/np/RADjlGIB8Vqt7NbG1kqzw-4aIV_k7nyIRirMhPKEYVSlc']
>>> # This URI has no retractions
>>>client.find_retractions_of('http://purl.org/np/RAeMfoa6I05zoUmK6sRypCIy3wIpTgS8gkum7vdfOamn8')
[]
```
