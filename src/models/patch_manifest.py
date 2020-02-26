import enum
import logging

from os import path as _path

from src.models.manifest import ManifestV1
from src.models.manifest_v2 import ManifestComparison

logger = logging.getLogger('twl')


class PatchType(enum.Enum):
    NONE = 0
    FUEL_PATCH = 1


class PatchFile:
    """
    This holds all information required for a patch file
    """

    def __init__(self, filename, path, target_hash, urls, size, target_hash_type='sha256',
                 patch_hash=None, patch_hash_type=None, patch_type=PatchType.NONE, patch_offset=0):
        self.filename = filename
        self.path = path
        self.patch_hash = patch_hash
        self.patch_hash_type = patch_hash_type
        self.target_hash = target_hash
        self.target_hash_type = target_hash_type
        self.patch_type = patch_type
        self.patch_offset = patch_offset
        self.urls = urls
        self.download_size = size


class PatchManifest:
    """
    Patch Manifest class
    """

    def __init__(self):
        self.dirs = set()
        self.files = list()

    @classmethod
    def from_v1_manifest(cls, manifest: ManifestV1):
        logger.debug('Creating PatchManifest from V1 DownloadManifest')
        patchmanifest = cls()
        patchmanifest.dirs = set(_path.dirname(file.path) for file in manifest.files)

        for v1_file in manifest.files:
            patchmanifest.files.append(PatchFile(
                filename=v1_file.filename, path=v1_file.path,
                target_hash=v1_file.hash.value, urls=v1_file.urls,
                size=v1_file.size
            ))

        return patchmanifest

    @classmethod
    def from_v2_manifest_comparison(cls, manifest_comparison: ManifestComparison,
                                    patches_result: list):
        """
        Builds PatchManifest from V2 ManifestComparison and result of patches request(s)

        Files without a URL (i.e. those filtered out before the patch request was made) will not be included.

        :param manifest_comparison: ManifestComparison
        :param patches_result: result of GetPatches request
        :return:
        """
        logger.debug('Creating PatchManifest for V2 Manifest')
        patchmanifest = cls()

        patches = dict()
        for patch in patches_result:
            patches[patch['targetHash']['value']] = patch

        for old_file, new_file in manifest_comparison.updated:
            path, filename = _path.split(new_file.path)
            patchmanifest.dirs.add(path)

            patch = patches[new_file.hash.value]

            patch_type = PatchType.NONE if patch['type'] == 'NONE' else PatchType.FUEL_PATCH

            patchmanifest.files.append(PatchFile(
                filename=filename, path=path,
                urls=patch['downloadUrls'], size=patch['size'],
                target_hash=new_file.hash.value,
                target_hash_type=new_file.hash.algorithm.lower(),
                patch_hash=patch['patchHash']['value'],
                patch_hash_type=patch['patchHash']['algorithm'].lower(),
                patch_type=patch_type
            ))

        for new_file in manifest_comparison.new:
            path, filename = _path.split(new_file.path)
            patchmanifest.dirs.add(path)

            patch = patches[new_file.hash.value]
            patchmanifest.files.append(PatchFile(
                filename=filename, path=path,
                urls=patch['downloadUrls'], size=patch['size'],
                target_hash=new_file.hash.value,
                target_hash_type=new_file.hash.algorithm.lower()
            ))

        return patchmanifest
