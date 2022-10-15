# Using the nanopublication's namespace
In a nanopublication you often want to refer to a concept that is not defined somewhere on the WWW. In that case it makes sense to make use of the namespace of the nanopublication itself, see for example this assertion that uses `nanopub-uri#timbernerslee` to refer to the concept Tim Berner's Lee.
```turtle
@prefix sub: <http://purl.org/np/RA_j6TPcnoQJ_XkISjugTgaRsFGLhpbZCC3mE7fXs0REI#> .

sub:assertion {
    sub:timbernerslee a <http://xmlns.com/foaf/0.1/Person> .
}
```
## Using blank nodes
But how do you make use of the nanopublication's namespace if you do not have access to the published nanopublication URI yet? We solve that by making use of blank nodes.

Upon publication, any blank nodes in the rdf graph are replaced with the nanopub's URI, with the blank node name as a fragment. For example, if the blank node is called 'timbernerslee', that would result in a URI composed of the nanopub's (base) URI, followed by #timbernslee. We can thus use blank nodes to refer to new concepts, making use of the namespace of the to-be-published URI.

An example:

```python
from rdflib import Graph, BNode, RDF, FOAF
from nanopub import Nanopub, NanopubConf, NanopubClient

my_assertion = Graph()

# We want to introduce a new concept in our publication: Tim Berners Lee
tim = BNode('timbernerslee')

# We assert that he is a person
my_assertion.add((tim, RDF.type, FOAF.Person) )

# Define the config for your nanopubs
np_conf = NanopubConf(
    add_prov_generated_time=True,
    add_pubinfo_generated_time=True,
    attribute_publication_to_profile=True,
)
# And create a nanopub object for this assertion
np = Nanopub(
    assertion=my_assertion,
	config=np_conf
)

# Let's publish this to the test server
client = NanopubClient(use_test_server=True)
np = client.publish(np)
print(np)
# Published to http://purl.org/np/RAdaZsPRcY5usXFKwSBfz9g-HOu-Bo1XmmhQc4g7uESgU
```
View the full nanopublication [here](http://purl.org/np/RAdaZsPRcY5usXFKwSBfz9g-HOu-Bo1XmmhQc4g7uESgU).

As you can see in the assertion, the 'timbernerslee' blank node is replaced with
a uri in the nanopublication's namespace:
```turtle
@prefix sub: <http://purl.org/np/RAdaZsPRcY5usXFKwSBfz9g-HOu-Bo1XmmhQc4g7uESgU#> .

sub:assertion {
    sub:timbernerslee a <http://xmlns.com/foaf/0.1/Person> .
}
```

## Introducing a concept
You can optionally specify that the Publication introduces a particular concept using blank nodes.

The pubinfo graph will note that this nanopub npx:introduces the concept. The concept should be a blank node (rdflib.term.BNode), and is converted to a URI derived from the nanopub's URI with a fragment (#) made from the blank node's name.

An example:
```python
import rdflib
from nanopub import Publication, NanopubClient

my_assertion = rdflib.Graph()

# We want to introduce a new concept in our publication: Tim Berners Lee
tim = rdflib.BNode('timbernerslee')

# We assert that he is a person
my_assertion.add((tim, rdflib.RDF.type, rdflib.FOAF.Person) )

# And create a nanopub introducing this new concept
np = Nanopub(
    assertion=my_assertion,
    introduces_concept=tim,
    config=NanopubConf(
        add_prov_generated_time=True,
        add_pubinfo_generated_time=True,
        attribute_publication_to_profile=True,
    )
)

# Let's publish this to the test server
client = NanopubClient(use_test_server=True)
client.publish(np)
print(np)
# Published to http://purl.org/np/RAq9gFEgxlOyG9SSDZ5DmBbyGet2z6pkrdWXIVYa6U6qI
# Published concept to http://purl.org/np/RAq9gFEgxlOyG9SSDZ5DmBbyGet2z6pkrdWXIVYa6U6qI#timbernerslee
```
View the full nanopublication [here](http://purl.org/np/RAq9gFEgxlOyG9SSDZ5DmBbyGet2z6pkrdWXIVYa6U6qI).

The publication info of the nanopublication denotes that this nanopublication introduces the 'timbernerslee' concept:
```turtle
@prefix npx: <http://purl.org/nanopub/x/> .
@prefix sub: <http://purl.org/np/RAq9gFEgxlOyG9SSDZ5DmBbyGet2z6pkrdWXIVYa6U6qI#> .
@prefix this: <http://purl.org/np/RAq9gFEgxlOyG9SSDZ5DmBbyGet2z6pkrdWXIVYa6U6qI> .

sub:pubinfo {
   this: npx:introduces sub:timbernerslee .
}
```
