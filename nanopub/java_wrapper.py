import shutil
import subprocess
from pathlib import Path
from typing import Union

import rdflib
import requests
from rdflib import ConjunctiveGraph, Literal
# from trustyuri.rdf.RdfHasher import make_hash
from nanopub.trustyuri.rdf import RdfHasher, RdfUtils
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from base64 import decodebytes, encodebytes

from nanopub.definitions import ROOT_FILEPATH, DUMMY_NAMESPACE, DUMMY_URI
from nanopub.namespaces import NPX
from nanopub.profile import PROFILE_INSTRUCTIONS_MESSAGE, Profile

NANOPUB_JAVA_SCRIPT = ('nanopub-java' if shutil.which('nanopub-java')  # In case installed with pip
                       else ROOT_FILEPATH / 'bin' / 'nanopub-java')  # In case of local dev

NANOPUB_TEST_SERVER = 'http://test-server.nanopubs.lod.labs.vu.nl/'


class JavaWrapper:
    """
    Wrapper around 'nanopub-java' java tool that is used to sign and publish nanopublications to
    a nanopub server.
    """

    def __init__(
            self,
            use_test_server: bool = False,
            explicit_private_key: str = None
        ):
        """Construct JavaWrapper.

        Args:
            use_test_server: Toggle using the test nanopub server.
        """
        self.use_test_server = use_test_server
        self.explicit_private_key = explicit_private_key

    @staticmethod
    def _run_command(command):
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

    def sign(self, unsigned_file: Union[str, Path]) -> str:
        unsigned_file = str(unsigned_file)
        args = ''
        if self.explicit_private_key:
            args = f'-k {self.explicit_private_key}'
        self._run_command(f'{NANOPUB_JAVA_SCRIPT} sign {unsigned_file} {args}')
        return self._get_signed_file(unsigned_file)


    def add_signature(self, g: ConjunctiveGraph, profile: Profile) -> ConjunctiveGraph:
        """Implementation in python of the process to sign with the private key"""
        # TODO: Add signature triples
        g.add((
            DUMMY_NAMESPACE["sig"],
            NPX["hasPublicKey"],
            Literal(profile.get_public_key()),
            DUMMY_NAMESPACE["pubInfo"],
        ))
        g.add((
            DUMMY_NAMESPACE["sig"],
            NPX["hasAlgorithm"],
            Literal("RSA"),
            DUMMY_NAMESPACE["pubInfo"],
        ))
        g.add((
            DUMMY_NAMESPACE["sig"],
            NPX["hasSignatureTarget"],
            DUMMY_URI,
            DUMMY_NAMESPACE["pubInfo"],
        ))
        # Normalize RDF
        # print("NORMED RDF STARTS")
        quads = RdfUtils.get_quads(g)
        normed_rdf = RdfHasher.normalize_quads(quads)
        print("NORMED RDF STARTS")
        print(normed_rdf)
        print("NORMED RDF END")

        # Signature signature = Signature.getInstance("SHA256withRSA");
        # https://stackoverflow.com/questions/55036059/a-java-server-use-sha256withrsa-to-sign-message-but-python-can-not-verify
        private_key = RSA.importKey(decodebytes(profile.get_private_key().encode()))
        signer = PKCS1_v1_5.new(private_key)
        signature_b = signer.sign(SHA256.new(normed_rdf.encode()))
        signature = encodebytes(signature_b).decode().replace("\n", "")
        print("SIGNATURE STARTS")
        print(signature)
        print("SIGNATURE ENDS")

        g.add((
            DUMMY_NAMESPACE["sig"],
            NPX["hasSignature"],
            Literal(signature),
            DUMMY_NAMESPACE["pubInfo"],
        ))

        return g

        # signed_g = ConjunctiveGraph()
        # signed_g.parse()
        # args = ''
        # if self.explicit_private_key:
        #     args = f'-k {self.explicit_private_key}'
        # self._run_command(f'{NANOPUB_JAVA_SCRIPT} sign {unsigned_file} {args}')
        # return self._get_signed_file(unsigned_file)

    # Implement sign/publish in python:
    # 1. Use trusty-uri lib to get the trusty URI
    # 2. Replace the temp nanopub URIs in the graph by the generated trusty URI
    # 3. Add signature in pubInfo (how to generate it?)
    # In java SignatureUtils > createSignedNanopub
    # 4. Publish to one of the np servers: https://monitor.petapico.org/
    # post.setEntity(new StringEntity(nanopubString, "UTF-8"));
    # post.setHeader("Content-Type", RDFFormat.TRIG.getDefaultMIMEType());

    def publish(self, signed: str):
        """Publish.

        Publish the signed nanopub to the nanopub server. Publishing to the real server depends
        on nanopub-java, for the test server we do a simple POST request.
        TODO: Use nanopub-java for publishing to test once it supports it.
        """
        args = ''
        if self.explicit_private_key:
            args = f'-k {self.explicit_private_key}'

        if self.use_test_server:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            with open(signed, 'rb') as data:
                r = requests.post(NANOPUB_TEST_SERVER, headers=headers, data=data)
            r.raise_for_status()
        else:
            self._run_command(f'{NANOPUB_JAVA_SCRIPT} publish {signed} {args}')
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

    def make_keys(self, path_name='~/.nanopub/id'):
        """
        Use nanopub-java to make the RSA keys for this user.
        By default, this uses the path name ~/.nanopub/id and produces a key-pair:
            ~/.nanopub/id_rsa and ~/.nanopub/id_rsa.pub

        NOTE THAT THE JAVA TOOL ADDS _rsa TO THE END OF YOUR PATH.
        """
        self._run_command(f'{NANOPUB_JAVA_SCRIPT} mkkeys -a RSA -f {path_name}')
