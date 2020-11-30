# Using the nanopublication's namespace
In a nanopublication you often want to refer to a concept that is not
defined somewhere on the WWW.
In that case it makes sense to make use of the namespace of the nanopublication itself, 
see for example this assertion that uses `nanopub-uri#timbernerslee` to refer
to the concept Tim Berner's Lee.
```
@prefix sub: <http://purl.org/np/RA_j6TPcnoQJ_XkISjugTgaRsFGLhpbZCC3mE7fXs0REI#> .

sub:assertion {
    sub:timbernerslee a <http://xmlns.com/foaf/0.1/Person> .
}
```
## Using blank nodes 
But how do you make use of the nanopublication's namespace if you do not have
access to the published nanopublication URI yet? We solve that by making use of
blank nodes.

Upon publication, any blank nodes in the rdf graph are replaced with the nanopub's URI, with the blank node name as a
fragment. For example, if the blank node is called 'timbernerslee', that would result in a URI composed of the
nanopub's (base) URI, followed by #timbernslee. We can thus use blank nodes to refer to new concepts, making use of the namespace of the 
to-be-published URI.

An example:

```python
>>> import rdflib
>>> from nanopub import Publication, NanopubClient
>>> 
>>> my_assertion = rdflib.Graph()
>>> 
>>> # We want to introduce a new concept in our publication: Tim Berners Lee
>>> tim = rdflib.BNode('timbernerslee')
>>> 
>>> # We assert that he is a person
>>> my_assertion.add((tim, rdflib.RDF.type, rdflib.FOAF.Person) )
>>> 
>>> # And create a publication object for this assertion
>>> publication = Publication.from_assertion(assertion_rdf=my_assertion)
>>> 
>>> # Let's publish this to the test server
>>> client = NanopubClient(use_test_server=True)
>>> client.publish(publication)
Published to http://purl.org/np/RA_j6TPcnoQJ_XkISjugTgaRsFGLhpbZCC3mE7fXs0REI
```
View the full nanopublication [here](http://test-server.nanopubs.lod.labs.vu.nl/RA_j6TPcnoQJ_XkISjugTgaRsFGLhpbZCC3mE7fXs0REI).

As you can see in the assertion, the 'timbernerslee' blank node is replaced with 
a uri in the nanopublication's namespace:
```
@prefix sub: <http://purl.org/np/RA_j6TPcnoQJ_XkISjugTgaRsFGLhpbZCC3mE7fXs0REI#> .

sub:assertion {
    sub:timbernerslee a <http://xmlns.com/foaf/0.1/Person> .
}
```

## Introducing a concept
You can optionally specify that the Publication introduces a 
particular concept using blank nodes. 
The pubinfo graph will note that this nanopub npx:introduces the concept.
The concept should be a blank node (rdflib.term.BNode), 
and is converted to a URI derived from the nanopub's URI 
with a fragment (#) made from the blank node's name.

An example:
```python
>>> import rdflib
>>> from nanopub import Publication, NanopubClient
>>> 
>>> my_assertion = rdflib.Graph()
>>> 
>>> # We want to introduce a new concept in our publication: Tim Berners Lee
>>> tim = rdflib.BNode('timbernerslee')
>>> 
>>> # We assert that he is a person
>>> my_assertion.add((tim, rdflib.RDF.type, rdflib.FOAF.Person) )
>>> 
>>> # We can create a publication introducing this new concept
>>> publication = Publication.from_assertion(assertion_rdf=my_assertion,
>>>                                          introduces_concept=tim)
>>> 
>>> # Let's publish this to the test server
>>> client = NanopubClient(use_test_server=True)
>>> client.publish(publication)
Published to http://purl.org/np/RAdpeRop9Ow5ArTRivUWkw7ArCI--J5K1vN3J9fw9gnuk
Published concept to http://purl.org/np/RAdpeRop9Ow5ArTRivUWkw7ArCI--J5K1vN3J9fw9gnuk#timbernerslee
```
Note that `NanopubClient.publish()` now also prints the published content URI.
View the full nanopublication [here](http://test-server.nanopubs.lod.labs.vu.nl/RAdpeRop9Ow5ArTRivUWkw7ArCI--J5K1vN3J9fw9gnuk).

The publication info of the nanopublication denotes that this nanopublication introduces the 'timbernerslee' concept:
```
@prefix npx: <http://purl.org/nanopub/x/> .
@prefix sub: <http://purl.org/np/RAdpeRop9Ow5ArTRivUWkw7ArCI--J5K1vN3J9fw9gnuk#> .
@prefix this: <http://purl.org/np/RAdpeRop9Ow5ArTRivUWkw7ArCI--J5K1vN3J9fw9gnuk> .

sub:pubInfo {
   this: npx:introduces sub:timbernerslee .
}
```
