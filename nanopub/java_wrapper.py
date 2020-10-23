import os
import subprocess
from pathlib import Path
from typing import Union

import rdflib

from nanopub.definitions import PKG_FILEPATH

# Location of nanopub tool (currently shipped along with the lib)
NANOPUB_SCRIPT = str(PKG_FILEPATH / 'np')


class JavaWrapper:
    """
    Wrapper around 'np' java tool that is used to sign and publish nanopublications to
    a nanopub server.
    """
    @staticmethod
    def _run_command(command):
        result = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
        rsa_key_messages = ['FileNotFoundException', 'id_rsa']
        stderr = result.stderr.decode('utf8')
        if all(m in stderr for m in rsa_key_messages):
            message = ('RSA key appears to be missing, see the instructions for making RSA keys'
                       'in the setup section of the README')
            raise RuntimeError(message)
        elif result.returncode != 0:
            raise RuntimeError(f'Error in nanopub java application: {stderr}')

    def sign(self, unsigned_file: Union[str, Path]) -> str:
        unsigned_file = str(unsigned_file)
        self._run_command(f'{NANOPUB_SCRIPT} sign ' + unsigned_file)
        return self._get_signed_file(unsigned_file)

    def publish(self, signed: str):
        self._run_command(f'{NANOPUB_SCRIPT} publish ' + signed)
        return self.extract_nanopub_url(signed)

    @staticmethod
    def extract_nanopub_url(signed: Union[str, Path]):
        # Extract nanopub URL
        # (this is pretty horrible, switch to python version as soon as it is ready)
        extracturl = rdflib.Graph()
        extracturl.parse(str(signed), format="trig")
        return dict(extracturl.namespaces())['this'].__str__()

    @staticmethod
    def _get_signed_file(unsigned_file: str):
        unsigned_file = Path(unsigned_file)

        return str(unsigned_file.parent / f'signed.{unsigned_file.name}')
