# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.8] - 2021-09-01

### Added
* Also publish sdist when publishing to pypi

## [1.2.7] - 2021-06-25

### Changed
* Prevent `setup_nanopub_profile` from ever overwriting key pair

### Fixed
* Pin `click` at version 7.1.2, as versions >8 break `setup_nanopub_profile`

## [1.2.6] - 2021-04-30

### Added
* Search result dicts now contain nanopublication label too, if provided by the grlc endpoint.

## [1.2.5] - 2021-03-05

### Fixed
* Fix bug that overwrites optional pubinfo and prov in `from_assertion()` calls.

## [1.2.4] - 2021-03-04

### Fixed
* Fix bug where user rdf was being mutated during publishing.

## [1.2.3] - 2021-02-05

### Added
* Added new `publication_attributed_to` argument to `Publication.from_assertion()`. Allows the `pubinfo` attribution to be manually set if desired.

## [1.2.2] - 2021-01-29

### Fixed
* Fix FileAlreadyExists bug in `setup_nanopub_profile`

## [1.2.1] - 2021-01-22

### Changed
* Rename `setup_profile` to `setup_nanopub_profile` to avoid ambiguity/clashes with other tools

### Fixed
* Make `nanopub` package compatible Windows operating system
* Added UTF-8 related flags to nanopub-java (in java call) to fix issues with certain characters on certain java builds
* Make regex in orcid validation accept ids ending with 'X'

## [1.2.0] - 2020-12-23

### Added
* Added Zenodo badge to README
* Pagination of results for search methods of `NanopubClient`

### Changed
* `nanopub-java` dependency is installed upon installation instead of upon runtime.
* search methods of `NanopubClient` return iterator instead of list


## [1.1.0] - 2020-12-17

### Added
* `.zenodo.json` for linking to zenodo
* `pubkey` option to methods of `NanopubClient` that allows searching for publications 
    signed with the given pubkey. For these methods:
    - `find_nanopubs_with_text`
    - `find_nanopubs_with_pattern`
    - `find_things`
* `filter_retracted` option to methods of `NanopubClient` that allows searching for publications 
    that are note retracted. For these methods:
    - `find_nanopubs_with_text`
    - `find_nanopubs_with_pattern`
    - `find_things`
* `NanopubClient.find_retractions_of` method to search retractions of a given nanopublication.
* `Publication.signed_with_public_key` property: the public key that the publication was signed with.
* `Publication.is_test_publication` property: denoting whether this is a publicaion on the test server.

### Changed
* Improved error message by pointing to documentation instead of Readme upon ProfileErrors

### Fixed
* Catch FileNotFoundError when profile.yml does not exist, raise ProfileError with useful messageinstead.
* Fixed broken link to documentation in README.md

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
