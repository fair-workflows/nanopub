# Retracting a nanopublication
A nanopublication is persistent, you can never edit nor delete it.
You can however retract a nanopublication.
This is done by publishing a new nanopublication that states that you
retract the original publication. You can use `NanopubClient.retract()`:
```python
>>> from nanopub import NanopubClient
>>> # Create the client (we use use_test_server=True to point to the test server)
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
