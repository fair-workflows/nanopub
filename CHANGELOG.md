# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2020-12-08

NB: All changes before [1.0.0] are collapsed in here (even though there were multiple pre-releases)
### Added
- `nanopub.client` module with the NanopubClient class that implements:
  * Searching (being a client with a direct (but incomplete) mapping to the nanopub server grlc endpoint):
    * `find_nanopubs_with_text` method
    * `find_nanopubs_with_pattern` method
    * `find_things` method
  * Fetching:
    * `fetch` method to fetch a nanopublication
  * Publishing:
    * Publish a statement using `claim` method
    * Publish a `Publication` object with `publish` method
  * Retracting:
    * Publish a retraction of an existing nanopublication created by this user (i.e. signed with same RSA key)
  
  * Test server functionality
    * Client can optionally be set to publish to (and fetch from) the nanopub test servers only.

- `nanopub.publication` module
  * `Publication` class to represent a nanopublication. 
  Includes `from_assertion` class method to construct a Publication object
  from an assertion graph
  * `replace_in_rdf` helper method to replace values in RDF
- `nanopub.java_wrapper` module, provides an interface to the nanopub-java tool for
  signing and publishing nanopublications.
- `nanopub.profile` module, getters and setters for the nanopub user profile
- `nanopub.setup_profile`, interactive command-line client to setup user profile
- `nanopub.namespaces`, often-used RDF namespaces
- `examples/`, holds a few notebooks that serve as examples of using the library
- User documentation
