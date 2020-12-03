# The nanopub test server
Throughout this documentation we make use of the 
[nanopub test server](http://test-server.nanopubs.lod.labs.vu.nl/)
by setting `use_test_server=True` when instantiating `NanopubClient`:
```python
>>> from nanopub import NanopubClient
>>> client = NanopubClient(use_test_server=True)
```
This will search and fetch from, and publish to the [nanopub test server](http://test-server.nanopubs.lod.labs.vu.nl/).

When learning about nanopub using the testserver is a good idea, because:
* You are free to experiment with publishing without polluting the production server.
* You can draft a publication and know exactly what it will look like on the nanopub server without polluting the production server.
* When searching (and to a lesser extent fetching) you are not putting an unnecessary load on the production server.

## Test purl URIs do not point to the test server
There is one caveat when using the test server that can be confusing:
The purl URI (for example: [http://purl.org/np/RA71u9tYPd7ZQifE_6hXjqVim6pkweuvjoi-8ehvLvzg8](http://server.nanopubs.lod.labs.vu.nl/RA71u9tYPd7ZQifE_6hXjqVim6pkweuvjoi-8ehvLvzg8))
points to the [nanopub production server](http://server.nanopubs.lod.labs.vu.nl/) 
resulting in a 404 page not found error.

A manual workaround is:
1. Open [http://purl.org/np/RA71u9tYPd7ZQifE_6hXjqVim6pkweuvjoi-8ehvLvzg8](http://purl.org/np/RA71u9tYPd7ZQifE_6hXjqVim6pkweuvjoi-8ehvLvzg8)
 in your browser
2. Notice that the URL changed to [http://server.nanopubs.lod.labs.vu.nl/RA71u9tYPd7ZQifE_6hXjqVim6pkweuvjoi-8ehvLvzg8](http://server.nanopubs.lod.labs.vu.nl/RA71u9tYPd7ZQifE_6hXjqVim6pkweuvjoi-8ehvLvzg8).
3. Replace 'server' with 'test-server': [http://test-server.nanopubs.lod.labs.vu.nl/RA71u9tYPd7ZQifE_6hXjqVim6pkweuvjoi-8ehvLvzg8](http://test-server.nanopubs.lod.labs.vu.nl/RA71u9tYPd7ZQifE_6hXjqVim6pkweuvjoi-8ehvLvzg8).

> **NB**: `NanopubClient.fetch()` does this for you if `use_test_server=True`.
