#! /usr/bin/env python3

import os
import shutil
from pathlib import Path
from typing import Union, Tuple

import click
from rdflib import Graph, FOAF, BNode, Literal

from nanopub import NanopubClient, Nanopub
from nanopub.definitions import USER_CONFIG_DIR
from nanopub.namespaces import NPX, ORCID
from nanopub.java_wrapper import JavaWrapper

PRIVATE_KEY_FILE = 'id_rsa'
PUBLIC_KEY_FILE = 'id_rsa.pub'
DEFAULT_PRIVATE_KEY_PATH = USER_CONFIG_DIR / PRIVATE_KEY_FILE
DEFAULT_PUBLIC_KEY_PATH = USER_CONFIG_DIR / PUBLIC_KEY_FILE
RSA = 'RSA'


@click.command()
@click.option('--keypair', nargs=2, type=Path,
              prompt=f'If the public and private key you would like to use are not in {USER_CONFIG_DIR}, '
                     f'provide them here. If they are in this directory or you wish to generate new keys, '
                     f'leave empty.',
              help='Your RSA public and private keys with which your nanopubs will be signed',
              default=None)
@click.option('--orcid', type=str, prompt=True, help='Your ORCID')
@click.option('--name', type=str, prompt=True, help='Your name')
@click.option('--publish/--no-publish', type=bool, is_flag=True, default=False,
              help='If true, nanopub will be published to nanopub servers',
              prompt='Would you like to publish your profile to the nanopub servers?')
def main(orcid, publish, name, keypair: Union[Tuple[Path, Path], None]):
    click.echo('Setting up nanopub profile...')

    if not USER_CONFIG_DIR.exists():
        USER_CONFIG_DIR.mkdir()

    if not keypair:
        if _rsa_keys_exist():
            if _check_erase_existing_keys():
                _delete_keys()
                JavaWrapper.make_keys()
                click.echo(f'Your RSA keys are stored in {USER_CONFIG_DIR}')
    else:
        public_key, private_key = keypair

        # Copy the keypair to the default location
        shutil.copy(public_key, USER_CONFIG_DIR / PUBLIC_KEY_FILE)
        shutil.copy(private_key, USER_CONFIG_DIR / PRIVATE_KEY_FILE)

        click.echo(f'Your RSA keys have been copied to {USER_CONFIG_DIR}')

    # Public key can always be found at DEFAULT_PUBLIC_KEY_PATH. Either new keys have been generated there or
    # existing keys have been copy to that location.
    public_key = DEFAULT_PUBLIC_KEY_PATH
    public_key = public_key.read_text()

    # Declare the user to nanopub
    if publish:
        assertion, concept = _declare_this_is_me(orcid, public_key, name)
        np = Nanopub.from_assertion(assertion, introduces_concept=concept)

        client = NanopubClient()
        client.publish(np)


def _delete_keys():
    os.remove(DEFAULT_PUBLIC_KEY_PATH)
    os.remove(DEFAULT_PRIVATE_KEY_PATH)


def _declare_this_is_me(orcid: str, public_key: str, name: str) -> Tuple[Graph, BNode]:
    # Construct your desired assertion (a graph of RDF triples)
    my_assertion = Graph()

    key_declaration = BNode('keyDeclaration')
    orcid_node = ORCID[orcid]

    my_assertion.add((key_declaration, NPX.declaredBy, orcid_node))
    my_assertion.add((key_declaration, NPX.hasAlgorithm, Literal(RSA)))
    my_assertion.add((key_declaration, NPX.hasPublicKey, Literal(public_key)))
    my_assertion.add((orcid_node, FOAF.name, Literal(name)))

    return my_assertion, key_declaration


def _rsa_keys_exist():
    return DEFAULT_PRIVATE_KEY_PATH.exists() or DEFAULT_PUBLIC_KEY_PATH


def _check_erase_existing_keys():
    return click.confirm('It seems you already have RSA keys for nanopub. Would you like to replace them?',
                         default=False)


if __name__ == '__main__':
    main()
