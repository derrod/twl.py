# Manifest v2 stuff

import lzma
import struct

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

import src.proto.sds_pb2 as sds


AMZ_RSA_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA6fSRMUi3VpTtv9P4+KvM
AcAIP4SYbTQfB1ns7vyUjsj8nrF2lGNtQTtGLnrNmM2ElZ2R7VmQtNiRtPMxToIW
Rajin0H0OyzGrHA8P6w96Mj4q1JeORCzJeVFgLOBClCCMmB+5bJBWnJcq/sEMwu9
gGynCeiYNLt7ZMVpL1GOsNjl+yLk7OMMGpMj1JWCVFfgYE9Lud1QZJllFAWhRBoT
wTctAUZTikObFUoBm+KEiCsKIcay4WOybvJwxTNBUl2GL8c+ihrT2ntLPpb9aIJE
/gXU3Ihl5oXe/0P/QN0CRu/ybXWLiGzIYqKIok4nepkdo8V3gWR55K801pOuck0B
awIDAQAB
-----END PUBLIC KEY-----'''


class HashV2:
    def __init__(self, message):
        self.value = message.value.hex()
        self.raw_value = message.value
        self.algorithm = sds.HashAlgorithm.Name(message.algorithm)


class Dir:
    def __init__(self, msg):
        self.mode = msg.mode
        self.path = msg.path


class FileV2:
    def __init__(self, msg):
        self.path = msg.path
        self.mode = msg.mode
        self.size = msg.size
        self.created = msg.created
        self.hash = HashV2(msg.hash)
        self.hidden = msg.hidden
        self.system = msg.system
        self.urls = None


class Package:
    def __init__(self, msg):
        self.name = msg.name
        self.files = [FileV2(sub_msg) for sub_msg in msg.files]
        self.dirs = [Dir(sub_msg) for sub_msg in msg.dirs]


class ManifestV2:
    """
    Manifest class, handles compreesion, verification, reading, etc.
    """
    __type__ = 'v2'
    _amz_rsa_key = RSA.importKey(AMZ_RSA_KEY)

    def __init__(self):
        self._header_pb = None
        self._manifest_pb = None
        self.packages = []

    def _decompress(self, content):
        if self._header_pb.compression.algorithm == sds.lzma:
            return lzma.decompress(content)
        elif self._header_pb.compression.algorithm == sds.none:
            return content
        else:
            raise ValueError('Unknown compression algorithm!')

    def _verify(self, manifest_content):
        if self._header_pb.signature.algorithm == sds.sha256_with_rsa:
            signer = PKCS1_v1_5.new(self._amz_rsa_key)
            digest = SHA256.new(manifest_content)
            return signer.verify(digest, self._header_pb.signature.value)
        else:
            raise ValueError('Unknown signature algorithm!')

    def read(self, content):
        header_size = struct.unpack('>I', content[:4])[0]
        self._header_pb = sds.ManifestHeader.FromString(content[4:4 + header_size])

        manifest_raw = self._decompress(content[4 + header_size:])
        if not self._verify(manifest_raw):
            raise ValueError('Signature verification failed')

        self._manifest_pb = sds.Manifest.FromString(manifest_raw)
        for package in self._manifest_pb.packages:
            self.packages.append(Package(package))

    @classmethod
    def create(cls, content):
        """
        Classmethod to create Manifest from binary data

        :param content: raw data received from Amazon SDS
        :return: Manifest class
        """
        c = cls()
        c.read(content)
        return c


class ManifestComparison:
    def __init__(self):
        self.new = []
        self.removed = []
        self.updated = []
    
    @classmethod
    def compare(cls, manifest, old_manifest=None):
        # 'Tv.Twitch.Fuel.Manifest.ManifestComparator' uses package 0, so let's just do the same.
        comparison = cls()
        if old_manifest:
            old_files = dict()
            for f in old_manifest.packages[0].files:
                old_files[f.path] = f

            for f in manifest.packages[0].files:
                if f.path not in old_files:
                    comparison.new.append(f)
                    continue

                if f.hash.value != old_files[f.path].hash.value:
                    comparison.updated.append((old_files[f.path], f))
                # delete files that are in old_files and new manifest from this dict
                del old_files[f.path]

            # all that remains are files that were removed!
            comparison.removed = old_files.values()
        else:
            # In this case there are just new files
            comparison.new = [f for f in manifest.packages[0].files]
        
        return comparison
