import getpass

import webbrowser
import requests

from urllib.parse import urlencode
from random import getrandbits


class TwitchAPI:
    tw_app_clientid = 'jf3xu125ejjjt5cl4osdjci6oz6p93r'
    tw_agent_clientid = 'rqbo1jq09v4pl4d16t85b3j4krvrvz'

    def __init__(self):
        self.token = None
        self.tw_user_data = dict()
        self.login_check_result = False
        self.session = requests.session()
        self.session.headers.update({
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': self.tw_agent_clientid
        })

    def send_login_req(self, json_data):
        r = self.session.post('https://passport.twitch.tv/login', json=json_data)
        j = r.json()
        return j

    def login_flow(self):
        post_data = {
            'client_id': self.tw_app_clientid,
            'undelete_user': False,
            'remember_me': True
        }

        use_backup_flow = False

        while True:
            user = input('Twitch username: ')
            pw = getpass.getpass('Twitch password: ')

            post_data['username'] = user
            post_data['password'] = pw

            while True:
                # Try login w/o 2FA
                j = self.send_login_req(post_data)

                if 'captcha_proof' in j:
                    post_data['captcha'] = dict(proof=j['captcha_proof'])

                if 'error_code' in j:
                    err_code = j['error_code']
                    if err_code == 3011 or err_code == 3012:  # missing 2fa token
                        if err_code == 3011:
                            print('Two factor authentication enabled, '
                                  'please enter token below and press [ENTER] to continue')
                        else:
                            print('Invalid two factor token, pleas try again.')

                        twofa = input('2FA token: ')
                        post_data['authy_token'] = twofa.strip()
                        continue

                    elif err_code == 3022:  # missing 2fa token
                        print('Twitch Guard code required, '
                              'please enter code below and press [ENTER] to continue')
                        twofa = input('Twitch Guard code from Email: ')
                        post_data['twitchguard_code'] = twofa.strip()
                        continue

                    elif err_code == 3001:  # invalid pw
                        print('Invalid username or password, please try again.')
                        break
                    elif err_code == 1000:
                        print('CLI login unavailable (CAPTCHA solving required), opening browser for manual auth...')
                        use_backup_flow = True
                        break
                    else:
                        print(f'Unknown error: {j}')
                        raise NotImplementedError(f'Unknown TwitchAPI error code: {err_code}')

                if 'access_token' in j:
                    self.token = j['access_token']
                    self.session.headers.update({'Authorization': f'OAuth {self.token}'})
                    return self.check_login()

            if use_backup_flow:
                break

        if use_backup_flow:
            self.token = self.login_flow_backup()
            self.session.headers.update({'Authorization': f'OAuth {self.token}'})
            return self.check_login()

        return False

    def check_login(self):
        if self.login_check_result:
            return self.login_check_result

        r = self.session.get('https://api.twitch.tv/kraken/user',
                             params=dict(api_client_id_killswitch='true'))

        if r.status_code == 200:
            self.tw_user_data = r.json()
            self.login_check_result = True

        return self.login_check_result

    def load_data(self, data):
        self.token = data['token']
        self.tw_user_data = data.get('userdata', None)
        if not self.tw_user_data:
            self.check_login()

    def export_data(self):
        return dict(token=self.token, userdata=self.tw_user_data)

    def login_flow_backup(self):
        """Backup OAUth login flow in case manual captcha solving is required"""
        url = 'https://id.twitch.tv/oauth2/authorize?'
        params = {
            'client_id': self.tw_agent_clientid,
            'login_type': 'login',
            'redirect_uri': 'https://twitch.tv/',
            'response_type': 'token',
            'scope': 'user_read',
            'state': '{:x}'.format(getrandbits(128))
        }
        webbrowser.open(url + urlencode(params))
        print('Enter the value of the "access_token" parameter from the URL you have been redirected to below')
        code = input('Access token: ')
        return code.strip()
