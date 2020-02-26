import logging
import requests

# from src.models.adg import DigitalGood
from src.models.manifest import ManifestV1
from src.models.manifest_v2 import ManifestV2

logger = logging.getLogger('twl')


class AmzSDS:
    url = 'https://sds.amazon.com/'

    def __init__(self):
        self.session = requests.session()
        self.session.headers.update({
            'Content-Encoding': 'amz-1.0'
        })

    def set_auth_data(self, twitch_token):
        self.session.headers.update({
            'Authorization': f'Bearer {twitch_token}',
            'TwitchOAuthToken': twitch_token,
            'x-auth-twitch': twitch_token,
        })

    def get_entitlements(self):
        req_headers = {
            'X-Amz-Target': 'com.amazonaws.gearbox.softwaredistribution.service.model.'
                            'SoftwareDistributionService.GetEntitlements'
        }

        req_body = {
            'clientId': 'Fuel',
            'syncPoint': None
        }
        r = self.session.post(self.url, json=req_body, headers=req_headers)
        return r.json()['entitlements']

    def get_versions(self, good_id):
        req_headers = {
            'X-Amz-Target': 'com.amazonaws.gearbox.softwaredistribution.service.model.'
                            'SoftwareDistributionService.GetVersions'
        }
        req_body = {
            'adgProductIds': [good_id],
            'Operation': 'GetVersions'
        }
        r = self.session.post(self.url, json=req_body, headers=req_headers)
        return r.json()['versions'][0]

    def get_download_manifest_v1(self, good_id):
        logger.debug(f'Requesting DownloadManifest (V1) for {good_id}')
        req_headers = {
            'X-Amz-Target': 'com.amazonaws.gearbox.softwaredistribution.service.model.'
                            'SoftwareDistributionService.GetDownloadManifest'
        }
        req_body = {
            'entitlementId': good_id
        }
        r = self.session.post(self.url, json=req_body, headers=req_headers)
        j = r.json()
        manifest_xml = j['manifest']
        logger.debug(f'Got Manifest version {j["versionId"]}')
        return ManifestV1.create(manifest_xml)

    def get_download_manifest_v2_info(self, good_id):
        logger.debug(f'Requesting DownloadManifest (V2) for {good_id}')
        req_headers = {
            'X-Amz-Target': 'com.amazonaws.gearbox.softwaredistribution.service.model.'
                            'SoftwareDistributionService.GetDownloadManifestV2'
        }
        req_body = {
            'adgGoodId': good_id,
            'Operation': 'GetDownloadManifestV2'
        }
        r = self.session.post(self.url, json=req_body, headers=req_headers)
        return r.json()

    def get_download_manifest_v2(self, good_id):
        j = self.get_download_manifest_v2_info(good_id)
        logger.debug(f'Got Manifest version {j["versionId"]}')
        dl_url = j['downloadUrls'][0]
        logger.debug(f'Downloading protobuf data from {dl_url}')
        r = self.session.get(dl_url)
        return ManifestV2.create(r.content)

    def get_patches(self, product_id, version, file_list, enable_delta=False):
        logger.debug(f'Requesting list of patches for {len(file_list)} files, delta enabled: {enable_delta}')
        req_headers = {
            'X-Amz-Target': 'com.amazonaws.gearbox.softwaredistribution.service.model.'
                            'SoftwareDistributionService.GetPatches'
        }
        req_body = {
            'Operation': 'GetPatches',
            'versionId': version,
            'fileHashes': file_list,
            'deltaEncodings': ['NONE'],
            'adgGoodId': product_id
        }
        if enable_delta:
            req_body['deltaEncodings'].append('FUEL_PATCH')

        r = self.session.post(self.url, json=req_body, headers=req_headers)
        j = r.json()
        return j['patches']
