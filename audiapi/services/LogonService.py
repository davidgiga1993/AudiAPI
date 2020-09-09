from typing import Dict
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from requests import RequestException

from Token import Token, TokenProvider
from model.UserInfo import UserInfo
from model.login.OpenIdConfig import OpenIdConfig
from services.Service import Service


class BrowserLoginResponse:
    def __init__(self, response: requests.Response, url: str):
        self.response = response  # type: requests.Response
        self.url = url  # type : str

    def get_location(self) -> str:
        """
        Returns the location the previous request redirected to
        """
        location = self.response.headers['Location']
        if location.startswith('/'):
            # Relative URL
            return BrowserLoginResponse.to_absolute(self.url, location)
        return location

    @classmethod
    def to_absolute(cls, absolute_url, relative_url) -> str:
        """
        Converts a relative url to an absolute url
        :param absolute_url: Absolute url used as baseline
        :param relative_url: Relative url (must start with /)
        :return: New absolute url
        """
        url_parts = urlparse(absolute_url)
        return url_parts.scheme + '://' + url_parts.netloc + relative_url


class LogonService(Service):
    """
    General API logon service
    (Audi ID)
    """

    CLIENT_ID = '09b6cbec-cd19-4589-82fd-363dfa8c24da@apps_vw-dilab_com'

    def login(self, user: str, password: str, persist_token: bool = True):
        """
        Creates a new session using the given credentials

        :param user: User
        :param password: Password
        :param persist_token: True if the token should be persisted in the file system after login
        """
        provider = self._login_request(user, password)
        self._api.set_token_provider(provider)
        if persist_token:
            provider.persist()

    def get_user_info(self) -> UserInfo:
        """
        Returns information about the current user.

        :return: User information
        """
        reply = self._api.get('https://identity-userinfo.vwgroup.io/oidc/userinfo', scope=None)
        return self._to_dto(reply, UserInfo())

    def restore_token(self) -> bool:
        """
        Tries to restore the latest persisted auth token

        :return: True if token could be restored
        """
        provider = TokenProvider.load()
        if provider is None or not provider.valid():
            return False
        self._api.set_token_provider(provider)
        return True

    def _get_open_id_config(self) -> OpenIdConfig:
        """
        Return the current open id configuration for audi
        """
        return self._to_dto(self._api.get('https://app-api.live-my.audi.com/myaudiappidk/v1/openid-configuration'),
                            OpenIdConfig())

    def _login_request(self, user: str, password: str) -> TokenProvider:
        """
        Requests a login token for the given user

        :param user: User
        :param password: Password
        :return: Token provider
        """
        open_id = self._get_open_id_config()
        login_code = self._browser_login(user, password, open_id)

        data = {
            'client_id': LogonService.CLIENT_ID,
            'grant_type': 'authorization_code',
            'response_type': 'token id_token',
            'code': login_code,
            'redirect_uri': 'myaudi:///',
        }
        reply = self._api.post('https://app-api.my.audi.com/myaudiappidk/v1/token', data=data, use_json=False)
        app_idk_token = Token.parse(reply)

        # Get the azs token, this token is used for car related requests
        data = {
            'config': 'myaudi',
            'grant_type': 'id_token',
            'stage': 'live',
            'token': app_idk_token.access_token
        }
        reply = self._api.post('https://app-api.live-my.audi.com/azs/v1/token', data=data)
        azs_token = Token.parse(reply)

        # MBB coauth token, first register the app
        data = {
            'appId': 'de.myaudi.mobile.assistant',
            'appName': 'myAudi',
            'appVersion': '3.20.0',
            'client_brand': 'Audi',
            'client_name': 'HTC U11',
            'platform': 'google'
        }
        reply = self._api.post('https://mbboauth-1d.prd.ece.vwg-connect.com/mbbcoauth/mobile/register/v1', data=data)
        client_id = reply['client_id']

        data = {
            'grant_type': 'id_token',
            'scope': 'sc2:fal',
            'token': app_idk_token.id_token
        }
        headers = {
            'X-Client-ID': client_id
        }
        reply = self._api.post('https://mbboauth-1d.prd.ece.vwg-connect.com/mbbcoauth/mobile/oauth2/v1/token',
                               data=data, headers=headers, use_json=False)
        mmb_token = Token.parse(reply)
        mmb_token.client_id = client_id

        provider = TokenProvider()
        provider.add_token(app_idk_token)
        provider.add_token(azs_token)
        provider.add_token(mmb_token)
        return provider

    def _browser_login(self, user: str, password: str, open_id: OpenIdConfig) -> str:
        """
        Logs into AUDI ID using the given username and password.
        The returned auth code can then be used to request a token for API access
        :param user: Username
        :param password: Password
        :param open_id: Open ID configuration
        :return: Authorization code
        """
        query_params = {
            'response_type': 'code',
            'client_id': LogonService.CLIENT_ID,
            'redirect_uri': 'myaudi:///',
            'scope': 'address profile badge birthdate birthplace nationalIdentifier nationality profession email '
                     'vin phone nickname name picture mbb gallery openid',
            'state': '7f8260b5-682f-4db8-b171-50a5189a1c08',
            'nonce': '583b9af2-7799-4c72-9cb0-e6c0f42b87b3',
            'prompt': 'login',
            'ui_locales': 'en-US en',
        }

        reply = self._api.get(open_id.authorization_endpoint, query_params=query_params, raw_reply=True,
                              allow_redirects=False)

        # Submit the email
        reply = self._emulate_browser(BrowserLoginResponse(reply, open_id.authorization_endpoint), {'email': user})
        # Submit the password
        reply = self._emulate_browser(reply, {'password': password})

        sso_url = reply.get_location()
        sso_reply = self._api.get(sso_url, raw_reply=True, allow_redirects=False)
        consent_url = BrowserLoginResponse(sso_reply, sso_url).get_location()
        consent_reply = self._api.get(consent_url, raw_reply=True, allow_redirects=False)
        success_url = BrowserLoginResponse(consent_reply, consent_url).get_location()
        success_reply = self._api.get(success_url, raw_reply=True, allow_redirects=False)

        my_audi_callback_url = success_reply.headers.get('location')
        query_strings = parse_qs(urlparse(my_audi_callback_url).query)
        return query_strings['code'][0]

    def _emulate_browser(self, reply: BrowserLoginResponse, form_data: Dict[str, str]) -> BrowserLoginResponse:
        # The reply redirects to the login page
        login_location = reply.get_location()
        page_reply = self._api.get(login_location, raw_reply=True)

        # Now parse the html body and extract the target url, csfr token and other required parameters
        html = BeautifulSoup(page_reply.content, 'html.parser')
        form_tag = html.find('form')

        form_inputs = html.find_all('input', attrs={'type': 'hidden'})
        for form_input in form_inputs:
            name = form_input.get('name')
            form_data[name] = form_input.get('value')

        # Extract the target url
        action = form_tag.get('action')
        if action.startswith('http'):
            # Absolute url
            username_post_url = action
        elif action.startswith('/'):
            # Relative to domain
            username_post_url = BrowserLoginResponse.to_absolute(login_location, action)
        else:
            raise RequestException('Unknown form action: ' + action)

        headers = {
            'referer': login_location
        }
        reply = self._api.post(username_post_url, form_data, headers=headers, use_json=False, raw_reply=True,
                               allow_redirects=False)
        return BrowserLoginResponse(reply, username_post_url)

    def _get_path(self):
        return 'https://id.audi.com'

    def _get_scope(self):
        return None


class MarketsService(Service):
    def _get_path(self):
        return None

    def _get_scope(self):
        return None

    def get_markets(self):
        """
        Returns all available countries and their languages

        :return: List of markets
        :rtype: dict(str, object)
        """
        markets = self._api.get('https://apps.audi.com/onetouch/configs/markets.json')
        return markets['countries']['countrySpecifications']
