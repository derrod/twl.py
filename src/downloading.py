import os

from src.models.patch_manifest import PatchManifest


class Downloader:
    """
    asyncio based patch downloader
    """
    pass


class Aria2Exporter:
    def __init__(self, base_path='', verify=False):
        self.base_path = base_path
        self.verify = verify
        self.is_windows = os.name == 'nt'

    def get_download_list(self, patchmanifest: PatchManifest):
        download_list = []

        for patchfile in patchmanifest.files:
            download_list.append(patchfile.urls[0])

            # Fix file paths for unix systems
            if not self.is_windows:
                patchfile.path = patchfile.path.replace('\\', '/')

            download_list.append('  dir={}'.format(os.path.join(self.base_path, patchfile.path)))
            download_list.append('  out={}'.format(patchfile.filename))

            if self.verify and patchfile.target_hash_type == 'sha256':
                download_list.append('  checksum=sha-256={}'.format(patchfile.target_hash))

        return '\n'.join(download_list)
