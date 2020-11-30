.. nanopub documentation master file, created by
   sphinx-quickstart on Thu Nov 26 14:29:07 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 1
   :hidden:

   what-are-nanopubs
   setup

.. toctree::
   :maxdepth: 1
   :caption: Publishing
   :hidden:

   publishing/publishing-nanopublications
   publishing/using-publication-namespace
   publishing/setting-subgraphs
   publishing/retraction

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Searching

   searching

Welcome to nanopub's documentation!
===================================
The ``nanopub`` library provides a high-level, user-friendly python
interface for searching, publishing and retracting nanopublications.

Nanopublications are a formalized and machine-readable way of communicating
the smallest possible units of publishable information.
See :doc:`../what-are-nanopubs` for more information.

Setup
-----

Install using pip:

::

    pip install nanopub

To publish to the nanopub server you need to setup your profile. This
allows the nanopub server to identify you. Run the following interactive
command:

::

    setup_profile

It will add and store RSA keys to sign your nanopublications, publish a
nanopublication with your name and ORCID iD to declare that you are
using using these RSA keys, and store your ORCID iD to automatically add
as author to the provenance of any nanopublication you will publish
using this library.

Quick Start
-----------

Publishing nanopublications
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import rdflib
    from nanopub import Publication, NanopubClient

    # Create the client (we use use_test_server=True to point to the test server)
    client = NanopubClient(use_test_server=True)

    # Either quickly publish a statement to the server
    client.claim('All cats are gray')

    # Or: 1. construct a desired assertion (a graph of RDF triples) using rdflib
    my_assertion = rdflib.Graph()
    my_assertion.add((rdflib.URIRef('www.example.org/timbernerslee'),
                      rdflib.RDF.type,
                      rdflib.FOAF.Person))

    # 2. Make a Publication object with this assertion
    publication = Publication.from_assertion(assertion_rdf=my_assertion)

    # 3. Publish the Publication object. The URI at which it is published is returned.
    publication_info = client.publish(publication)
    print(publication_info)

Searching for nanopublications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from nanopub import NanopubClient

    # Create the client
    client = NanopubClient()

    # Search for all nanopublications containing the text 'fair'
    results = client.find_nanopubs_with_text('fair')
    print(results)


Fetching nanopublications and inspecting them
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from nanopub import NanopubClient

    # Create the client
    client = NanopubClient()

    # Fetch the nanopublication at the specified URI
    publication = client.fetch('http://purl.org/np/RApJG4fwj0szOMBMiYGmYvd5MCtRle6VbwkMJUb1SxxDM')

    # Print the RDF contents of the nanopublication
    print(publication)

    # Iterate through all triples in the assertion graph
    for s, p, o in publication.assertion:
        print(s, p, o)
