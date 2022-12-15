import os
import subprocess
import tempfile
from base64 import decodebytes
from pathlib import Path

import rdflib
from Crypto.PublicKey import RSA
from rdflib import ConjunctiveGraph

from nanopub.definitions import ROOT_FILEPATH
from nanopub.namespaces import NP
from nanopub.nanopub import Nanopub
from nanopub.profile import PROFILE_INSTRUCTIONS_MESSAGE

# nanopub-java is only used in dev or tests when the repo is cloned
NANOPUB_JAVA_SCRIPT = (ROOT_FILEPATH / 'scripts' / 'nanopub-java')


class JavaWrapper:
    """
    Wrapper around 'nanopub-java' java tool that is used to sign and publish nanopublications to
    a nanopub server.
    """

    def __init__(self, private_key: str = None) -> None:
        """Construct JavaWrapper.

        Args:
            use_test_server: Toggle using the test nanopub server.
        """
        if private_key:
            # Put keys in files (needed for nanopub-java)
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
        unsigned_path = Path(unsigned_file)
        return str(unsigned_path.parent / f'signed.{unsigned_path.name}')
