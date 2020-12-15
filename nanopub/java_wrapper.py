import subprocess
from pathlib import Path
from typing import Union

import rdflib
import requests

from nanopub.definitions import PKG_FILEPATH

from nanopub.profile import PROFILE_INSTRUCTIONS_MESSAGE

# Location of nanopub tool (currently shipped along with the lib)
NANOPUB_SCRIPT = str(PKG_FILEPATH / 'np')
NANOPUB_TEST_SERVER = 'http://test-server.nanopubs.lod.labs.vu.nl/'


class JavaWrapper:
    """
    Wrapper around 'np' java tool that is used to sign and publish nanopublications to
    a nanopub server.
    """

    def __init__(self, use_test_server=False):
        """Construct JavaWrapper.

        Args:
            use_test_server: Toggle using the test nanopub server.
        """
        self.use_test_server = use_test_server

    @staticmethod
    def _run_command(command):
        result = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
        rsa_key_messages = ['FileNotFoundException', 'id_rsa']
        stderr = result.stderr.decode('utf8')
        if all(m in stderr for m in rsa_key_messages):
            raise RuntimeError('Nanopub RSA key appears to be missing,\n'
                               + PROFILE_INSTRUCTIONS_MESSAGE)
        elif result.returncode != 0:
            raise RuntimeError(f'Error in nanopub java application: {stderr}')

    def sign(self, unsigned_file: Union[str, Path]) -> str:
        unsigned_file = str(unsigned_file)
        self._run_command(f'{NANOPUB_SCRIPT} sign ' + unsigned_file)
        return self._get_signed_file(unsigned_file)

    def publish(self, signed: str):
        """ Publish.

        Publish the signed nanopub to the nanopub server. Publishing to the real server depends
        on nanopub-java, for the test server we do a simple POST request.

        TODO: Use nanopub-java for publishing to test once it supports it.
        """
        if self.use_test_server:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            with open(signed, 'rb') as data:
                r = requests.post(NANOPUB_TEST_SERVER, headers=headers, data=data)
            r.raise_for_status()
        else:
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

    @staticmethod
    def make_keys(path_name='~/.nanopub/id'):
        """
        Use nanopub-java to make the RSA keys for this user.
        By default, this uses the path name ~/.nanopub/id and produces a key-pair:
            ~/.nanopub/id_rsa and ~/.nanopub/id_rsa.pub

        NOTE THAT THE JAVA TOOL ADDS _rsa TO THE END OF YOUR PATH.
        """
        subprocess.run([NANOPUB_SCRIPT, 'mkkeys', '-a', 'RSA', '-f', path_name], check=True)
