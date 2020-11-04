#! /usr/bin/env python3
import yaml
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
PROFILE_PATH = USER_CONFIG_DIR / 'profile.yml'
RSA = 'RSA'


@click.command(help='Interactive CLI to create a nanopub user profile. A local version of the profile will be stored '
                    'in the '
                    'user config dir (by default HOMEDIR/.nanopub/). The profile will also be published to the '
                    'nanopub servers.')
@click.option('--keypair', nargs=2, type=Path,
              prompt=f'If the public and private key you would like to use are not in {USER_CONFIG_DIR}, '
                     f'provide them here. If they are in this directory or you wish to generate new keys, '
                     f'leave empty.',
              help='Your RSA public and private keys with which your nanopubs will be signed',
              default=None)
@click.option('--orcid', type=str, prompt=True, help='Your ORCID')
@click.option('--name', type=str, prompt=True, help='Your name')
@click.option('--publish/--no-publish', type=bool, is_flag=True, default=True,
              help='If true, nanopub will be published to nanopub servers',
              prompt=('Would you like to publish your profile to the nanopub servers?'
                      'this links your ORCID to your RSA key, thereby making all your'
                      'publications linkable to you'))
def main(orcid, publish, name, keypair: Union[Tuple[Path, Path], None]):
    """
    Interactive CLI to create a user profile.

    :param orcid: the users orcid or other form of universal identifier
    :param publish: if True, profile will be published to nanopub servers
    :param name: the name of the user
    :param keypair: a tuple containing the paths to the public and private RSA key to be used to sign nanopubs. If
                    empty, new keys will be generated.
    :return:
    """
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
            JavaWrapper.make_keys()
            click.echo(f'Your RSA keys are stored in {USER_CONFIG_DIR}')
    else:
        public_key_path, private_key = keypair

        # Copy the keypair to the default location
        shutil.copy(public_key_path, USER_CONFIG_DIR / PUBLIC_KEY_FILE)
        shutil.copy(private_key, USER_CONFIG_DIR / PRIVATE_KEY_FILE)

        click.echo(f'Your RSA keys have been copied to {USER_CONFIG_DIR}')

    # Public key can always be found at DEFAULT_PUBLIC_KEY_PATH. Either new keys have been generated there or
    # existing keys have been copy to that location.
    public_key_path = DEFAULT_PUBLIC_KEY_PATH
    public_key = public_key_path.read_text()

    profile_nanopub_uri = None

    # Declare the user to nanopub
    if publish:
        assertion, concept = _create_this_is_me_rdf(orcid, public_key, name)
        np = Nanopub.from_assertion(assertion, introduces_concept=concept)

        client = NanopubClient()
        result = client.publish(np)

        profile_nanopub_uri = result['concept_uri']

    # Keys are always stored or copied to default location
    _store_profile(name, orcid, public_key_path, DEFAULT_PRIVATE_KEY_PATH, profile_nanopub_uri)


def _store_profile(name: str, orcid: str, public_key: Path, private_key: Path, profile_nanopub_uri: str = None):
    profile = {'name': name, 'orcid': orcid, "public_key": str(public_key), 'private_key': str(private_key)}

    if profile_nanopub_uri:
        profile['profile_nanopub'] = profile_nanopub_uri

    with PROFILE_PATH.open('w') as f:
        yaml.dump(profile, f)

    click.echo(f'Stored profile in {str(PROFILE_PATH)}')


def _delete_keys():
    os.remove(DEFAULT_PUBLIC_KEY_PATH)
    os.remove(DEFAULT_PRIVATE_KEY_PATH)


def _create_this_is_me_rdf(orcid: str, public_key: str, name: str) -> Tuple[Graph, BNode]:
    """
    Create a set of RDF triples declaring the existence of the user with associated ORCID.

    :param orcid:
    :param public_key:
    :param name:
    :return:
    """
    my_assertion = Graph()

    key_declaration = BNode('keyDeclaration')
    orcid_node = ORCID[orcid]

    my_assertion.add((key_declaration, NPX.declaredBy, orcid_node))
    my_assertion.add((key_declaration, NPX.hasAlgorithm, Literal(RSA)))
    my_assertion.add((key_declaration, NPX.hasPublicKey, Literal(public_key)))
    my_assertion.add((orcid_node, FOAF.name, Literal(name)))

    return my_assertion, key_declaration


def _rsa_keys_exist():
    return DEFAULT_PRIVATE_KEY_PATH.exists() or DEFAULT_PUBLIC_KEY_PATH.exists()


def _check_erase_existing_keys():
    return click.confirm('It seems you already have RSA keys for nanopub. Would you like to replace them?',
                         default=False)


if __name__ == '__main__':
    main()
