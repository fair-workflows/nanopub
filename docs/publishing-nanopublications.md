# Publishing nanopublications
The `nanopub` library provides an intuitive API that makes publishing nanopublications much easier. 
The rationale is that you often do not want to worry about the details of composing 
the RDF that is often the same in each nanopublication. Instead you should focus on the 
content of your nanopublication: the assertion.

## Prerequisits for publishing
Before you can publish you should [setup your profile](../setup#setup-your-profile)

## Quickly publishing nanopublications using `claim`
You can quickly publish a nanopublicaiton with a single simple statement using the `claim` method:
```python
>>> from nanopub import NanopubClient

>>> # Create the client (we use use_test_server=True to point to the test server)
>>> client = NanopubClient(use_test_server=True)

>>> # Publish a simple statement to the server
>>> client.claim('All cats are gray')
Published to http://purl.org/np/RAcTwW_JdTqZJTXA4jUTFUj6ut8OI9AqaPb1IBPsLsy-o
```
You can [view](http://test-server.nanopubs.lod.labs.vu.nl/RAcTwW_JdTqZJTXA4jUTFUj6ut8OI9AqaPb1IBPsLsy-o)
the resulting nanopublication on the nanopub test server. (NB: the purl link actually
points to the 'production' nanopub server, so we manually need to look at the test server: 
[http://test-server.nanopubs.lod.labs.vu.nl](http://test-server.nanopubs.lod.labs.vu.nl))

The generated RDF makes use of the Hypotheses and Claims Ontology ([HYCL](http://purl.org/petapico/o/hycl))

This is the assertion part of the nanopublication, denoting the statement:
```
@prefix hycl: <http://purl.org/petapico/o/hycl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sub: <http://purl.org/np/RAcTwW_JdTqZJTXA4jUTFUj6ut8OI9AqaPb1IBPsLsy-o#> .

sub:assertion {
    sub:mystatement a hycl:Statement ;
        rdfs:label "All cats are gray" .
}
```

The provenance part of the nanopublication denotes that the ORCID iD from the profile claimed the
statement:
```
@prefix hycl: <http://purl.org/petapico/o/hycl#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sub: <http://purl.org/np/RAcTwW_JdTqZJTXA4jUTFUj6ut8OI9AqaPb1IBPsLsy-o#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

sub:provenance {
    sub:assertion prov:generatedAtTime "2020-11-30T09:44:38.809739"^^xsd:dateTime ;
        prov:wasAttributedTo <https://orcid.org/0000-0000-0000-0000> .

    <https://orcid.org/0000-0000-0000-0000> hycl:claims sub:mystatement .
}
```
 
## A simple recipe for publishing RDF triples
You can use `Publication` objects to easily publish nanopublications with your assertion 
(think of the assertion as the content of your nanopublication).

This is a 3-step recipe that works for most cases:
 1) Construct a desired assertion using [`rdflib`](https://rdflib.readthedocs.io/en/stable/).
 2) Make a `Publication` object using the assertion, making use of `Publication.from_assertion()`.
 3) Publish the `Publication` object using `NanopubClient.publish()`.
 
Here is a minimal example:
```python
>>> import rdflib
>>> from nanopub import NanopubClient, Publication
>>> 
>>> # Create the client (we use use_test_server=True to point to the test server)
>>> client = NanopubClient(use_test_server=True)
>>> 
>>> # 1. construct a desired assertion (a graph of RDF triples) using rdflib
>>> my_assertion = rdflib.Graph()
>>> my_assertion.add((rdflib.URIRef('www.example.org/timbernerslee'),
>>>                   rdflib.RDF.type,
>>>                   rdflib.FOAF.Person))
>>> 
>>> # 2. Make a Publication object with this assertion
>>> publication = Publication.from_assertion(assertion_rdf=my_assertion)
>>> 
>>> # 3. Publish the Publication object.
>>> publication_info = client.publish(publication)
Published to http://purl.org/np/RAkRcU_0FtVYLiFQ07D9tVLNL7nrHr8XT75fa790bd_vI
```
You can [view](http://test-server.nanopubs.lod.labs.vu.nl/RAkRcU_0FtVYLiFQ07D9tVLNL7nrHr8XT75fa790bd_vI)
the resulting nanopublication on the nanopub test server. (NB: the purl link actually
points to the 'production' nanopub server, so we manually need to look at the test server: 
[http://test-server.nanopubs.lod.labs.vu.nl](http://test-server.nanopubs.lod.labs.vu.nl))

This is the resulting assertion part of the nanopublication:
```
@prefix sub: <http://purl.org/np/RAkRcU_0FtVYLiFQ07D9tVLNL7nrHr8XT75fa790bd_vI#> .

sub:assertion {
    <https://www.example.org/timbernerslee> a <http://xmlns.com/foaf/0.1/Person> .
}
```

The library automatically adds relevant RDF triples for the provenance part of the nanopublication:
```
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sub: <http://purl.org/np/RAkRcU_0FtVYLiFQ07D9tVLNL7nrHr8XT75fa790bd_vI#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

sub:provenance {
    sub:assertion prov:generatedAtTime "2020-11-30T11:48:26.417427"^^xsd:dateTime .
}
```
as well as for the publication info part of the nanopublication:
```
@prefix npx: <http://purl.org/nanopub/x/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sub: <http://purl.org/np/RAkRcU_0FtVYLiFQ07D9tVLNL7nrHr8XT75fa790bd_vI#> .
@prefix this: <http://purl.org/np/RAkRcU_0FtVYLiFQ07D9tVLNL7nrHr8XT75fa790bd_vI> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

sub:pubInfo {
    sub:sig npx:hasAlgorithm "RSA" ;
        npx:hasPublicKey "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmso7vmRO/Cp4Pt0RkJJkV5qfc1WFYU/jMtkdxxb5+lfIVXNV97XQnM1Tj4fkb/W6jkP6fHl8mj8Q7hl7VgUnQ6I+B7cMGpxW9Z8Br+JNx8DPMMt08VCH5+JMENPRKl91r7rF/YPWCAgL9eqXSixCNMNAj5RBmMTQoPuRkpgmt1wIDAQAB" ;
        npx:hasSignature "H9U/gpNX0nWgyqBjTTKD1/WdjDk4j9eTaF+Kzxym4haYORnz6jhDoC7hKnSGgs+Gc/puFn5XeokjLrXronRrTWkYU8orpGNK9sMkNnGkXzLBSgJBmCervpAt8XNAUevHNtJiVhRiMKIo6Tw+xO2yTsoFV8Qj9uUjGLuPnUg8Isw=" ;
        npx:hasSignatureTarget this: .

    this: prov:generatedAtTime "2020-11-30T11:48:26.417427"^^xsd:dateTime ;
        prov:wasAttributedTo <https://orcid.org/0000-0000-0000-0000> .
}
```
