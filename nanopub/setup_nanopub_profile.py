#! /usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
from typing import Union, Tuple

import click
import rdflib

from nanopub import Publication, NanopubClient, namespaces
from nanopub.definitions import USER_CONFIG_DIR
from nanopub.java_wrapper import JavaWrapper
from nanopub.profile import Profile, store_profile

PRIVATE_KEY_FILE = 'id_rsa'
PUBLIC_KEY_FILE = 'id_rsa.pub'
DEFAULT_KEYS_PATH_PREFIX = USER_CONFIG_DIR / 'id'
DEFAULT_PRIVATE_KEY_PATH = USER_CONFIG_DIR / PRIVATE_KEY_FILE
DEFAULT_PUBLIC_KEY_PATH = USER_CONFIG_DIR / PUBLIC_KEY_FILE
RSA = 'RSA'
ORCID_ID_REGEX = r'^https://orcid.org/(\d{4}-){3}\d{4}$'


def validate_orcid_id(ctx, orcid_id: str):
    """
    Check if valid ORCID iD, should be https://orcid.org/ + 16 digit in form:
        https://orcid.org/0000-0000-0000-0000
    """
    if re.match(ORCID_ID_REGEX, orcid_id):
        return orcid_id
    else:
        raise ValueError('Your ORCID iD is not valid, please provide a valid ORCID iD that '
                         'looks like: https://orcid.org/0000-0000-0000-0000')


@click.command(help='Interactive CLI to create a nanopub user profile. '
                    'A local version of the profile will be stored in the user config dir '
                    '(by default HOMEDIR/.nanopub/). '
                    'The profile will also be published to the nanopub servers.')
@click.option('--keypair', nargs=2, type=Path,
              prompt=f'If the public and private key you would like to use are not '
                     f'in {USER_CONFIG_DIR}, provide them here. '
                     f'If they are in this directory or you wish to generate new keys, '
                     f'leave empty.',
              help='Your RSA public and private keys with which your nanopubs will be signed',
              default=None)
@click.option('--orcid_id', type=str,
              prompt='What is your ORCID iD (i.e. https://orcid.org/0000-0000-0000-0000)?',
              help='Your ORCID iD (i.e. https://orcid.org/0000-0000-0000-0000)',
              callback=validate_orcid_id)
@click.option('--name', type=str, prompt='What is your full name?', help='Your full name')
@click.option('--publish/--no-publish', type=bool, is_flag=True, default=True,
              help='If true, nanopub will be published to nanopub servers',
              prompt=('Would you like to publish your profile to the nanopub servers? '
                      'This links your ORCID iD to your RSA key, thereby making all your '
                      'publications linkable to you'))
def main(orcid_id, publish, name, keypair: Union[Tuple[Path, Path], None]):
    """
    Interactive CLI to create a user profile.

    Args:
        orcid_id: the users ORCID iD or other form of universal identifier. Example:
            `https://orcid.org/0000-0000-0000-0000`
        publish: if True, profile will be published to nanopub servers
        name: the name of the user
        keypair: a tuple containing the paths to the public and private RSA key to be used to sign
            nanopubs. If empty, new keys will be generated.
    """
    click.echo('Setting up nanopub profile...')

    if not USER_CONFIG_DIR.exists():
        USER_CONFIG_DIR.mkdir()

    if not keypair:
        if _rsa_keys_exist():
            if _check_erase_existing_keys():
                _delete_keys()
                JavaWrapper.make_keys(path_name=DEFAULT_KEYS_PATH_PREFIX)
                click.echo(f'Your RSA keys are stored in {USER_CONFIG_DIR}')
        else:
            JavaWrapper.make_keys(path_name=DEFAULT_KEYS_PATH_PREFIX)
            click.echo(f'Your RSA keys are stored in {USER_CONFIG_DIR}')
    else:
        public_key_path, private_key = keypair

        # Copy the keypair to the default location
        shutil.copy(public_key_path, USER_CONFIG_DIR / PUBLIC_KEY_FILE)
        shutil.copy(private_key, USER_CONFIG_DIR / PRIVATE_KEY_FILE)

        click.echo(f'Your RSA keys have been copied to {USER_CONFIG_DIR}')

    # Public key can always be found at DEFAULT_PUBLIC_KEY_PATH.
    # Either new keys have been generated there or
    # existing keys have been copy to that location.
    public_key = DEFAULT_PUBLIC_KEY_PATH.read_text()

    profile = Profile(orcid_id, name, DEFAULT_PUBLIC_KEY_PATH, DEFAULT_PRIVATE_KEY_PATH)
    store_profile(profile)

    # Declare the user to nanopub
    if publish:
        assertion, concept = _create_this_is_me_rdf(orcid_id, public_key, name)
        np = Publication.from_assertion(assertion, introduces_concept=concept,
                                        assertion_attributed_to=orcid_id)

        client = NanopubClient()
        result = client.publish(np)

        profile.nanopub_uri = result['concept_uri']

        # Store profile nanopub uri
        store_profile(profile)


def _delete_keys():
    os.remove(DEFAULT_PUBLIC_KEY_PATH)
    os.remove(DEFAULT_PRIVATE_KEY_PATH)


def _create_this_is_me_rdf(orcid_id: str, public_key: str, name: str
                           ) -> Tuple[rdflib.Graph, rdflib.BNode]:
    """
    Create a set of RDF triples declaring the existence of the user with associated ORCID iD.
    """
    assertion = rdflib.Graph()
    assertion.bind('foaf', rdflib.FOAF)
    assertion.bind("npx", namespaces.NPX)

    key_declaration = rdflib.BNode('keyDeclaration')
    orcid_node = rdflib.URIRef(orcid_id)

    assertion.add((key_declaration, namespaces.NPX.declaredBy, orcid_node))
    assertion.add((key_declaration, namespaces.NPX.hasAlgorithm, rdflib.Literal(RSA)))
    assertion.add((key_declaration, namespaces.NPX.hasPublicKey, rdflib.Literal(public_key)))
    assertion.add((orcid_node, rdflib.FOAF.name, rdflib.Literal(name)))

    return assertion, key_declaration


def _rsa_keys_exist():
    return DEFAULT_PRIVATE_KEY_PATH.exists() or DEFAULT_PUBLIC_KEY_PATH.exists()


def _check_erase_existing_keys():
    return click.confirm('It seems you already have RSA keys for nanopub. '
                         'Would you like to replace them?',
                         default=False)


if __name__ == '__main__':
    main()
