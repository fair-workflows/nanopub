import os
from pathlib import Path
from typing import Union

import rdflib

from nanopub.definitions import PKG_FILEPATH

# Location of nanopub tool (currently shipped along with the lib)
NANOPUB_SCRIPT = str(PKG_FILEPATH / 'np')


def _shell_command(command):
    if os.system(command) != 0:
        raise Exception(f'Shell command failed: {command}')


def sign(unsigned_file: Union[str, Path]) -> str:
    unsigned_file = str(unsigned_file)
    _shell_command(f'{NANOPUB_SCRIPT} sign ' + unsigned_file)

    return _get_signed_file(unsigned_file)


def publish(signed: str):
    _shell_command(f'{NANOPUB_SCRIPT} publish ' + signed)

    return extract_nanopub_url(signed)


def extract_nanopub_url(signed: Union[str, Path]):
    # Extract nanopub URL
    # (this is pretty horrible, switch to python version as soon as it is ready)
    extracturl = rdflib.Graph()
    extracturl.parse(str(signed), format="trig")
    return dict(extracturl.namespaces())['this'].__str__()


def _get_signed_file(unsigned_file: str):
    unsigned_file = Path(unsigned_file)

    return str(unsigned_file.parent / f'signed.{unsigned_file.name}')
