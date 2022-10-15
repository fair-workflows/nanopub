from base64 import decodebytes, encodebytes

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from rdflib import BNode, ConjunctiveGraph, Literal, Namespace, URIRef

from nanopub.definitions import FINAL_NANOPUB_URI, NANOPUB_SERVER_LIST, NP_TEMP_PREFIX, MalformedNanopubError, log
from nanopub.namespaces import NPX
from nanopub.profile import Profile
from nanopub.trustyuri.rdf import RdfHasher, RdfUtils
from nanopub.trustyuri.rdf.RdfPreprocessor import transform


def add_signature(g: ConjunctiveGraph, profile: Profile, dummy_namespace: Namespace) -> ConjunctiveGraph:
    """Implementation in python of the process to sign with a private key"""
    g.add((
        dummy_namespace["sig"],
        NPX["hasPublicKey"],
        Literal(profile.public_key),
        dummy_namespace["pubinfo"],
    ))
    g.add((
        dummy_namespace["sig"],
        NPX["hasAlgorithm"],
        Literal("RSA"),
        dummy_namespace["pubinfo"],
    ))
    g.add((
        dummy_namespace["sig"],
        NPX["hasSignatureTarget"],
        dummy_namespace[""],
        dummy_namespace["pubinfo"],
    ))
    # Normalize RDF
    quads = RdfUtils.get_quads(g)
    normed_rdf = RdfHasher.normalize_quads(
        quads,
        baseuri=str(dummy_namespace),
        hashstr=" "
    )
    # Note: normed_rdf needs to end with a newline
    # print(f"NORMED RDF STARTS\n{normed_rdf}\nNORMED RDF ENDS")

    # Sign the normalized RDF with the private RSA key
    private_key = RSA.importKey(decodebytes(profile.private_key.encode()))
    signer = PKCS1_v1_5.new(private_key)
    signature_b = signer.sign(SHA256.new(normed_rdf.encode()))
    signature = encodebytes(signature_b).decode().replace("\n", "")
    log.debug(f"Nanopub signature: {signature}")

    # Add the signature to the graph
    g.add((
        dummy_namespace["sig"],
        NPX["hasSignature"],
        Literal(signature),
        dummy_namespace["pubinfo"],
    ))

    # Generate the trusty URI
    quads = RdfUtils.get_quads(g)
    trusty_artefact = RdfHasher.make_hash(
        quads,
        baseuri=str(dummy_namespace),
        hashstr=" "
    )
    log.debug(f"Trusty artefact: {trusty_artefact}")

    g = replace_trusty_in_graph(trusty_artefact, str(dummy_namespace), g)
    return g


def replace_trusty_in_graph(trusty_artefact: str, dummy_ns: str, graph: ConjunctiveGraph):
    if str(dummy_ns).startswith(NP_TEMP_PREFIX):
        # Replace with http://purl.org/np/ if the http://purl.org/nanopub/temp/
        # prefix is used in the dummy nanopub URI
        np_uri = FINAL_NANOPUB_URI + trusty_artefact
    else:
        np_uri = dummy_ns + trusty_artefact

    graph.bind("this", Namespace(np_uri))
    graph.bind("sub", Namespace(np_uri + "#"))

    bnodemap: dict = {}
    for s, p, o, c in graph.quads():
        if c:
            g = c.identifier
        else:
            raise Exception("Found a nquads without graph when replacing dummy URIs with trusty URIs. Something went wrong.")
        new_g = URIRef(transform(g, trusty_artefact, dummy_ns, bnodemap))
        new_s = URIRef(transform(s, trusty_artefact, dummy_ns, bnodemap))
        new_p = URIRef(transform(p, trusty_artefact, dummy_ns, bnodemap))
        new_o = o
        if isinstance(o, URIRef) or isinstance(o, BNode):
            new_o = URIRef(transform(o, trusty_artefact, dummy_ns, bnodemap))

        graph.remove((s, p, o, g))
        graph.add((new_s, new_p, new_o, new_g))
    return graph


def publish_graph(g: ConjunctiveGraph, use_server: str = NANOPUB_SERVER_LIST[0]) -> bool:
    """Publish a nanopub.

    Publish the signed nanopub to the nanopub server we do a simple POST request.
    """
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    log.info(f"Publishing to nanopub server {use_server}")
    headers = {'Content-Type': 'application/trig'}
    data = g.serialize(format="trig")
    r = requests.post(use_server, headers=headers, data=data)
    r.raise_for_status()
    # if r.status_code == 201:
    return True


def verify_trusty(g: ConjunctiveGraph, source_uri: str, source_namespace: Namespace) -> bool:
    source_trusty = source_uri.split('/')[-1]
    quads = RdfUtils.get_quads(g)
    expected_trusty = RdfHasher.make_hash(
        quads,
        baseuri=str(source_namespace),
        hashstr=" "
    )
    if expected_trusty != source_trusty:
        raise MalformedNanopubError(f"The Trusty artefact of the nanopub {source_trusty} is not valid. It should be {expected_trusty}")
    else:
        return True


def verify_signature(g: ConjunctiveGraph, source_uri: str, source_namespace: Namespace) -> bool:
    # Get public key from the triples
    pubkey_uri = URIRef(f"{source_uri}#sig")
    pubkey = ''
    for s, p, o in g.triples((pubkey_uri, NPX.hasPublicKey, None)):
        pubkey = str(o)

    # Get signature from the triples
    signature_uri = URIRef(f"{source_uri}#sig")
    signature = ''
    for s, p, o in g.triples((signature_uri, NPX.hasSignature, None)):
        signature = str(o)
    # g.remove((signature_uri, NPX.hasSignature, None))

    quads = RdfUtils.get_quads(g)
    normed_rdf = RdfHasher.normalize_quads(
        quads,
        baseuri=str(source_namespace),
        hashstr=" "
    )

    key = RSA.import_key(decodebytes(str(pubkey).encode()))
    hash_value = SHA256.new(normed_rdf.encode())
    verifier = PKCS1_v1_5.new(key)
    try:
        verifier.verify(hash_value, decodebytes(signature.encode()))
        return True
    except Exception as e:
        raise MalformedNanopubError(e)
