import os
import subprocess
from pathlib import Path
from typing import Union

import rdflib

from nanopub.definitions import PKG_FILEPATH

# Location of nanopub tool (currently shipped along with the lib)
NANOPUB_SCRIPT = str(PKG_FILEPATH / 'np')


def _run_command(command):
    result = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    rsa_key_messages = ['FileNotFoundException', 'id_rsa']
    stderr = result.stderr.decode('utf8')
    if all(m in stderr for m in rsa_key_messages):
        message = ('RSA key appears to be missing, see the instructions for making RSA keys in the '
                   'setup section of the README')
        raise RuntimeError(message)
    elif result.returncode != 0:
        raise RuntimeError(f'Error in nanopub java application: {stderr}')


def sign(unsigned_file: Union[str, Path]) -> str:
    unsigned_file = str(unsigned_file)
    _run_command(f'{NANOPUB_SCRIPT} sign ' + unsigned_file)

    return _get_signed_file(unsigned_file)


def publish(signed: str):
    _run_command(f'{NANOPUB_SCRIPT} publish ' + signed)

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
