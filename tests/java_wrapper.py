import shutil
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Union

import rdflib
import requests
from rdflib import ConjunctiveGraph, Literal, URIRef
from nanopub.nanopub import Nanopub
# from trustyuri.rdf.RdfHasher import make_hash
from nanopub.trustyuri.rdf import RdfHasher, RdfUtils
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from base64 import decodebytes, encodebytes

from nanopub.definitions import ROOT_FILEPATH, DUMMY_NAMESPACE, DUMMY_URI, FINAL_NANOPUB_URI
from nanopub.namespaces import NP
from nanopub.profile import PROFILE_INSTRUCTIONS_MESSAGE, Profile

# NANOPUB_JAVA_SCRIPT = ('nanopub-java' if shutil.which('nanopub-java')  # In case installed with pip
#                        else ROOT_FILEPATH / 'bin' / 'nanopub-java')  # In case of local dev

NANOPUB_JAVA_SCRIPT = (ROOT_FILEPATH / 'bin' / 'nanopub-java')

NANOPUB_TEST_SERVER = 'http://test-server.nanopubs.lod.labs.vu.nl/'


class JavaWrapper:
    """
    Wrapper around 'nanopub-java' java tool that is used to sign and publish nanopublications to
    a nanopub server.
    """

    def __init__(
            self,
            # use_test_server: bool = False,
            private_key: str = None
        ):
        """Construct JavaWrapper.

        Args:
            use_test_server: Toggle using the test nanopub server.
        """
        # self.use_test_server = use_test_server
        if private_key:
            # Work around to put keys in files (needed for nanopub-java)
            keys_dir = tempfile.mkdtemp()
            private_key_path = os.path.join(keys_dir, "id_rsa")
            with open(private_key_path, "w") as f:
                f.write(private_key + '\n')
            self.private_key = str(private_key_path)

            public_key_path = os.path.join(keys_dir, "id_rsa.pub")
            key = RSA.importKey(decodebytes(private_key.encode()))
            public_key = key.publickey().export_key().decode('utf-8').replace("-----BEGIN PUBLIC KEY-----\n", "").replace("-----END PUBLIC KEY-----", "")
            with open(public_key_path, "w") as f:
                f.write(public_key)
        # print(self.private_key)


    def _run_command(self, command):
        result = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
        rsa_key_messages = ['FileNotFoundException', 'id_rsa']
        stderr = result.stderr.decode('utf8')
        if all(m in stderr for m in rsa_key_messages):
            raise RuntimeError('Nanopub RSA key appears to be missing,\n'
                               + PROFILE_INSTRUCTIONS_MESSAGE
                               + '\nDetailed error message:\n' + stderr)
        elif all(m in stderr for m in ['SignatureException', 'Seems to have signature']):
            raise RuntimeError('The Publication you are trying to publish already has a signature, '
                               'this means it is likely already published. '
                               'If you want to publish a modified existing nanopublication '
                               'you need to do a few extra steps before you can publish. '
                               'See the discussion in: '
                               'https://github.com/fair-workflows/nanopub/issues/110')
        elif result.returncode != 0:
            raise RuntimeError(f'Error in nanopub-java when running {command}: {stderr}')


    def sign(self, np: Nanopub) -> str:
        tmp_dir = tempfile.mkdtemp()
        unsigned_file = os.path.join(tmp_dir, "unsigned.trig")
        with open(unsigned_file, "w") as f:
            f.write(np.rdf.serialize(format="trig"))

        unsigned_file = str(unsigned_file)
        args = ''
        if self.private_key:
            args = f'-k {self.private_key}'

        cmd = f'{NANOPUB_JAVA_SCRIPT} sign {unsigned_file} {args}'
        # print(cmd)
        self._run_command(cmd)
        signed_file = self._get_signed_file(unsigned_file)
        g = ConjunctiveGraph()
        g.parse(signed_file, format="trig")
        source_uri = str(list(
            g.subjects(
                predicate=rdflib.RDF.type, object=NP.Nanopublication
            )
        )[0])
        return source_uri


    def _get_signed_file(self, unsigned_file: str):
        unsigned_file = Path(unsigned_file)
        return str(unsigned_file.parent / f'signed.{unsigned_file.name}')



    # def publish(self, signed: str):
    #     """Publish.

    #     Publish the signed nanopub to the nanopub server. Publishing to the real server depends
    #     on nanopub-java, for the test server we do a simple POST request.
    #     TODO: Use nanopub-java for publishing to test once it supports it.
    #     """
    #     args = ''
    #     if self.private_key:
    #         args = f'-k {self.private_key}'

    #     if self.use_test_server:
    #         headers = {'content-type': 'application/x-www-form-urlencoded'}
    #         with open(signed, 'rb') as data:
    #             r = requests.post(NANOPUB_TEST_SERVER, headers=headers, data=data)
    #         r.raise_for_status()
    #     else:
    #         print("Java publishing disabled since python does it")
    #         # self._run_command(f'{NANOPUB_JAVA_SCRIPT} publish {signed} {args}')
    #     return self.extract_nanopub_url(signed)

    # @staticmethod
    # def extract_nanopub_url(signed: Union[str, Path]):
    #     # Extract nanopub URL
    #     # (this is pretty horrible, switch to python version as soon as it is ready)
    #     extracturl = rdflib.Graph()
    #     extracturl.parse(str(signed), format="trig")
    #     return dict(extracturl.namespaces())['this'].__str__()

    # def make_keys(self, path_name='~/.nanopub/id'):
    #     """
    #     Use nanopub-java to make the RSA keys for this user.
    #     By default, this uses the path name ~/.nanopub/id and produces a key-pair:
    #         ~/.nanopub/id_rsa and ~/.nanopub/id_rsa.pub

    #     NOTE THAT THE JAVA TOOL ADDS _rsa TO THE END OF YOUR PATH.
    #     """
    #     self._run_command(f'{NANOPUB_JAVA_SCRIPT} mkkeys -a RSA -f {path_name}')
