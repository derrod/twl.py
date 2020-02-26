#!/usr/bin/env python3

import argparse
import json
import logging
import os

import src.utils as utils

from src.apis.amazon_api import AmzSDS
from src.apis.twitch_api import TwitchAPI
from src.downloading import Aria2Exporter
from src.logger import setup_custom_logger
from src.models.manifest_v2 import ManifestComparison, ManifestV2
from src.models.patch_manifest import PatchManifest, PatchType
from src.models.sds import GetPatchesHashPairBuilder
from src.patching import Patcher

logger = setup_custom_logger('twl')
logger.setLevel(logging.INFO)

# ToDo implement CLI UI
# Todo rewrite this temporary thing to use subparsers
config_path = os.path.expanduser(os.sep.join(['~', 'twl.json']))
cache_path = os.path.expanduser(os.sep.join(['~', 'twl_game_cache.json']))


class TwlClient:
    def __init__(self, disable_ssl_verify=False):
        self.twitch_api_client = TwitchAPI()
        self.amz_sds = AmzSDS()
        self.twl_config = dict(install_dir='', installed_games=dict(),
                               data_dir='')
        self.fuel_authenticated = False

        # For Debugging only!
        if disable_ssl_verify:
            self.twitch_api_client.session.verify = False
            self.amz_sds.session.verify = False

    @property
    def authenticated(self):
        return self.twitch_api_client.check_login()

    def auth(self):
        if not self.twitch_api_client.token:
            self.twitch_api_client.login_flow()
        if self.authenticated:
            twl.save_config(config_path)

    def fuel_auth(self):
        if self.fuel_authenticated:
            return
        fuel_token = self.twitch_api_client.token
        self.amz_sds.set_auth_data(fuel_token)
        self.fuel_authenticated = True

    def fuel_get_games(self, force_refresh=False):
        if not self.authenticated:
            twl.auth()
        if not self.fuel_authenticated:
            twl.fuel_auth()

        entitlements = []

        try:
            entitlements = json.load(open(cache_path))
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warn('Loading cached product database failed, fetching from API')
            force_refresh = True

        if force_refresh:
            entitlements = twl.amz_sds.get_entitlements()
            json.dump(entitlements, open(cache_path, 'w'), indent=2, sort_keys=True)

        return entitlements

    def fuel_get_manifest(self, good_id, installed=False, version=1):
        if not self.authenticated:
            twl.auth()
        if not self.fuel_authenticated:
            twl.fuel_auth()

        if version == 1:
            return self.amz_sds.get_download_manifest_v1(good_id)
        else:
            if installed:
                raise NotImplementedError
            return self.amz_sds.get_download_manifest_v2(good_id)

    def fuel_get_v2_patchmanifest(self, game, manifest_comparison: ManifestComparison, delta_enabled=False):
        # Technically we could just get the version from GetManifestV2,
        # we just replicate what the real app does here.
        # (And also I cba to make it possible to get the version info as well)
        version_info = self.amz_sds.get_versions(game['product']['id'])

        logger.info('Getting list of Patches/Download URLs, this can take some '
                    'time depending on how many files the game install has.')
        hash_pair_generator = GetPatchesHashPairBuilder(manifest_comparison)
        hash_pair_generator.max_hashpairs_per_request = 1000
        patches = []
        for hash_pair in hash_pair_generator.get_next_hashes():
            patches.extend(self.amz_sds.get_patches(game['id'], version_info['versionId'],
                                                    hash_pair, delta_enabled))

        return PatchManifest.from_v2_manifest_comparison(manifest_comparison, patches)

    def load_config(self, config_file=config_path):
        if not os.path.exists(config_file):
            logger.error('Config file does not exist!')
            return
        config_data = json.load(open(config_file))
        self.twl_config = config_data['twl_data']
        if 'twitch_data' in config_data:
            self.twitch_api_client.load_data(config_data['twitch_data'])

    def save_config(self, config_file=config_path):
        config_data = dict(
            twitch_data=self.twitch_api_client.export_data(),
            twl_data=self.twl_config
        )
        json.dump(config_data, open(config_file, 'w'), indent=2, sort_keys=True)


if __name__ == '__main__':
    logger.info('TwitchLauncher.py version <placeholder>')
    parser = argparse.ArgumentParser(description='Twitch Launcher in python!')

    # Functions
    group = parser.add_mutually_exclusive_group()
    group.required = True
    group.add_argument('--auth', action='store_true', default=False,
                       dest='action_auth', help='Authenticate with Twitch')
    group.add_argument('--list', action='store_true', default=False,
                       dest='action_list', help='List games owned by account')
    group.add_argument('--install', action='store_true', default=False,
                       dest='action_intall', help='Install game')
    group.add_argument('--checkupdates', action='store_true', default=False,
                       dest='action_checkupdates', help='Check for game updates')
    group.add_argument('--update', action='store_true', default=False,
                       dest='action_update', help='Update selected game')
    group.add_argument('--debug', action='store_true', default=False,
                       dest='action_debug', help='Run debug code')

    # Install options
    parser.add_argument('--game-id', action='store', dest='game_id',
                        help='Install location')
    parser.add_argument('--install-dir', action='store', dest='install_dir',
                        default='', help='Full Install location')
    parser.add_argument('--install-base-dir', action='store', dest='install_base_dir',
                        default='', help='Install Base location')
    parser.add_argument('--disable-v2-manifest', action='store_true', dest='disable_v2_manifest', default=False,
                        help='Disable usage of V2 manifests (may be faster but can fail for big games)')
    parser.add_argument('--aria2c', action='store_true', default=False, dest='export_aria2c',
                        help='Generate aria2c download file instead')
    parser.add_argument('--aria2c-file', action='store', dest='export_aria2c_file',
                        help='Path/filename of aria2c download file')
    parser.add_argument('--aria2c-disable-verify', action='store_false', default=True, dest='aria2c_verify',
                        help='Disables file integrity verification information in aria2c file')
    parser.add_argument('--ignore-dx-redists', action='store_true', default=False, dest='ignore_dx_redist',
                        help='Do not download DirectX redistributables')

    # Update options
    parser.add_argument('--verify', action='store_true', dest='update_verify',
                        help='Verify game files after update')
    parser.add_argument('--enable-delta-patches', action='store_true', dest='use_patches',
                        help='Enable use of Delta Patches instead of downloading full files (untested)')

    # List options
    parser.add_argument('--show-all', action='store_true', default=False, dest='list_show_all',
                        help='Show all products on accounts (including non-games)')
    parser.add_argument('--sort', action='store_true', default=False, dest='list_sort',
                        help='Sort prodcuts by name rather than using the order they were fetched from the API')

    # Download options
    parser.add_argument('-t', action='store', dest='download_threads',
                        help='Number of download jobs to run in parallel')

    # General options
    parser.add_argument('-v', action='store_true', default=False,
                        dest='verbose', help='Set loglevel to debug')
    parser.add_argument('--disable-ssl-verify', action='store_true', default=False,
                        dest='disable_ssl', help='Disable SSL verification on HTTPS connections (for Debugging)')

    args = parser.parse_args()

    twl = TwlClient(disable_ssl_verify=args.disable_ssl)
    twl.load_config(config_path)

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.action_auth:
        if not twl.twitch_api_client.token:
            twl.auth()
            logger.info('Authentication complete!')
        else:
            logger.error('Auth token already exists! Use --deauth to remove existing login.')
    elif args.action_list:
        products = twl.fuel_get_games(force_refresh=True)
        print('Products registered to your account:')

        if not args.list_show_all:
            products = [product for product in products if product['product']['productLine'] == 'Twitch:FuelGame']

        if args.list_sort:
            products = sorted(products, key=lambda a: a['product']['title'])

        for good in products:
            if good['product']['asinVersion'] > 0:
                idstr = "ASIN: %s" % good['product']['asin']
            else:
                idstr = "ID: %s" % good['product']['id']

            print(f'* {good["product"]["productLine"]}, Name: "{good["product"]["title"]}", {idstr}')

        print(f'Total: {len(products)}', 'Products' if args.list_show_all else 'Games')

    elif args.action_intall:
        if not args.game_id:
            logger.critical('Missing --game-id parameter')
            exit(1)

        if args.export_aria2c and not args.export_aria2c_file:
            logger.critical('Missing aria2c downloadlist filename!')
            exit(1)

        twl.auth()
        products = twl.fuel_get_games()
        # Filter out non-games
        products = [product for product in products if product['product']['productLine'] == 'Twitch:FuelGame']

        if ',' in args.game_id and args.export_aria2c:
            logger.info('Multiple games specified, aria2c output file will contain all of them!')
            games = args.game_id.split(',')
        elif args.game_id == 'ALL':
            games = [product['product']['id'] for product in products]
        else:
            games = [args.game_id]

        for game_id in games:
            game = None
            for game in products:
                if game['product']['id'] == game_id or game['product']['asin'] == game_id:
                    break

            if not game:
                logger.critical('Could not find game specified!')
                exit(1)

            game_title = game["product"]["title"]
            logger.info(f'Fetching info for game: {game_title}')

            if args.export_aria2c:
                logger.info('Exporting to aria2c download list...')
                install_path = args.install_dir
                if not install_path:
                    install_path = os.path.join(args.install_base_dir, utils.clean_path(game_title))

                a2e = Aria2Exporter(base_path=install_path,
                                    verify=args.aria2c_verify)

                if args.disable_v2_manifest:
                    dl_manifest = twl.fuel_get_manifest(game['id'], version=1)
                    patch_manifest = PatchManifest.from_v1_manifest(dl_manifest)
                else:
                    dl_manifest = twl.fuel_get_manifest(game['id'], version=2)
                    mc = ManifestComparison.compare(dl_manifest)

                    # Remove DirectX redists
                    if args.ignore_dx_redist:
                        to_delete = []
                        for index, f in enumerate(mc.new):
                            if '/' in f.path:
                                last_dir = f.path.rsplit('/')[-2]
                                if last_dir.lower() == 'directx':
                                    to_delete.append(index)
                        for i in reversed(to_delete):
                            del mc.new[i]

                    patch_manifest = twl.fuel_get_v2_patchmanifest(game, mc)

                total_size = sum(f.download_size for f in patch_manifest.files) / 1024. / 1024.
                logger.info(f'Read Manifest: {len(patch_manifest.files)} files, {total_size:.02f} Megabytes in total')

                download_list = a2e.get_download_list(patch_manifest)
                with open(args.export_aria2c_file, 'a' if len(games) > 1 else 'w') as f:
                    f.write(download_list)
                    f.write('\n')

                logger.info(f'To install run: aria2c -i "{args.export_aria2c_file}" --file-allocation=none -j 20 -V -c')
            else:
                # mc = ManifestComparison.compare(v2_manifest, old_manifest)
                raise NotImplementedError
    elif args.action_checkupdates:
        raise NotImplementedError
    elif args.action_update:
        raise NotImplementedError
    elif args.action_debug:
        ## Okay so this is the wild west of old crap and testing shit
    
        test_download = False
        test_patching = False
        test_other_stuff = False
        patch_test_path = '/tmp/twitch/hld_patches/{}'

        if test_download:
            # This was to test patching/updating with delta patches
            # we first fetch the manifest for the version of Hyper Light Drifter, then modify the second one to contain the hashes of the old version I still had installed
            # We then create the diff between the manifests (based on hashes) and request a patch manifest.
            # Finally, download the delta patches from the CDN and save them to disk
            manifest = twl.fuel_get_manifest('68b4033a-ca5a-04d1-2b62-b5fb7b61d517', version=2)
            manifest_2 = twl.fuel_get_manifest('68b4033a-ca5a-04d1-2b62-b5fb7b61d517', version=2)

            # read sha256 file of old install and update manifest accordingly.
            l = [l.strip().split(' *') for l in open('/tmp/twitch/Hyper Light Drifter_old.sha256', 'r').readlines()]
            file_hash_map = dict()
            for fhash, path in l:
                file_hash_map[path[20:]] = fhash

            for f in manifest_2.packages[0].files:
                new_hash = file_hash_map[f.path.replace('/', '\\')]
                f.hash.value = new_hash

            mc = ManifestComparison.compare(manifest, manifest_2)
            # id is the version, product.id is the product id from the entitlement list (I think)
            game = dict(id='68b4033a-ca5a-04d1-2b62-b5fb7b61d517',
                        product=dict(id='b515a0c1-b73d-4201-aae3-1ef8fb1faf5e'))
            patch_manifest = twl.fuel_get_v2_patchmanifest(game, mc, delta_enabled=True)
            print('Files to update/patch:', len(patch_manifest.files))

            for patch_file in patch_manifest.files:
                if patch_file.patch_type == PatchType.NONE:
                    continue

                if patch_file.path:
                    f_path = patch_test_path.format('{}/{}.patch'.format(patch_file.path, patch_file.filename))
                else:
                    f_path = patch_test_path.format('{}.patch'.format(patch_file.filename))

                if os.path.exists(f_path):
                    continue

                print('Downloading patch file for', patch_file.filename, '...')
                r = twl.amz_sds.session.get(patch_file.urls[0])

                with open(f_path, 'wb') as f:
                    f.write(r.content)

        if test_patching:
            # Test to make sure the delta patching works using the previosuly downloaded patch file
            patcher = Patcher(open(patch_test_path.format('HyperLightDrifter.exe'), 'rb'),
                              open(patch_test_path.format('HyperLightDrifter.exe.patch'), 'rb'),
                              open(patch_test_path.format('HyperLightDrifter.exe.new'), 'wb'))
            logger.info('Starting patcher...')
            patcher.run()
            logger.info('Done!')

    twl.save_config(config_path)

