import json
from json import JSONDecodeError
from typing import Dict, Optional

import requests

from audiapi.Token import TokenProvider


class API:
    """
    Wrapper for the audi API
    """
    BASE_HEADERS = {'Accept': 'application/json',
                    'X-App-Name': 'myAudi',
                    'X-App-Version': '3.20.0',
                    'User-Agent': 'okhttp/4.7.2',
                    }
    """
      'X-App-ID': 'de.audi.mmiapp',
                    
                    'X-Brand': 'audi',
                    'X-Country-Id': 'DE',
                    'X-Language-Id': 'de',
                    'X-Platform': 'google',"""

    def __init__(self, proxy=None):
        """
        Creates a new API

        :param proxy: Proxy which should be used in the URL format e.g. http://proxy:8080
        """
        self._token_provider = TokenProvider()  # type: TokenProvider

        if proxy is not None:
            self.__proxy = {'http': proxy,
                            'https': proxy}
        else:
            self.__proxy = None

        self._lang = None  # type: Optional[str]
        self._country = None  # type: str

        self._session = requests.Session()
        """
        Holds the current web session. This is required for keeping the cookies
        during the login process
        """

    def set_market(self, country: str, language: str):
        """
        Sets the market area that should be used
        :param country: country (e.g. DE)
        :param language: Language (e.g. de)
        """
        self._lang = language
        self._country = country

    def set_token_provider(self, token_provider: TokenProvider):
        """
        Sets the token provider that should be used for authorization

        :param token_provider: Token
        """
        self._token_provider = token_provider

    def get(self, url, query_params: Dict[str, str] = None, raw_reply: bool = False, scope: str = None, **kwargs):
        return self._api_call(self._session.get, url, scope, params=query_params, raw_reply=raw_reply,
                              **kwargs)

    def put(self, url: str, data=None, headers: Dict[str, str] = None, scope: str = None, **kwargs):
        return self._api_call(self._session.put, url, scope, data, headers, **kwargs)

    def post(self, url: str, data=None, headers: Dict[str, str] = None, scope: str = None,
             use_json: bool = True, raw_reply: bool = False, **kwargs):
        return self._api_call(self._session.post, url, scope, data, headers, use_json, raw_reply, **kwargs)

    def _api_call(self, method, url: str, scope: str, data=None, headers: Dict[str, str] = None,
                  use_json: bool = True, raw_reply: bool = False, **kwargs):

        final_headers = self._get_headers(scope, headers)
        if use_json and data is not None:
            data = json.dumps(data)
            final_headers['content-type'] = 'application/json'

        r = method(url, data=data,
                   headers=final_headers,
                   proxies=self.__proxy,
                   **kwargs)
        if raw_reply:
            return r
        return self._handle_response(r)

    @staticmethod
    def _handle_response(response):
        if response.status_code == 404:
            raise Exception('Unknown endpoint - 404: ' + response.url)
        try:
            data = response.json()
        except JSONDecodeError:
            print('Error while decoding response: ' + str(response.text))
            raise

        if response.status_code == 403:
            # Sometimes the error is in "code" and "message"
            error_code = data.get('code')
            error_msg = data.get('message')
            raise Exception('API error: ' + str(error_code) + '\n' + error_msg)

        error = data.get('error')
        if error is not None:
            if isinstance(error, str):
                error_msg = data.get('error_description', '')
            else:
                error_msg = error.get('description', '')
            raise Exception('API error: ' + str(error) + '\n' + error_msg)
        return data

    def _get_headers(self, scope: str, headers: Dict[str, str] = None):
        if headers is not None:
            full_headers = headers
        else:
            full_headers = dict()

        token = self._token_provider.get_token(scope)
        if token is not None:
            full_headers['Authorization'] = 'Bearer ' + token.access_token
            if token.client_id is not None:
                full_headers['X-Client-ID'] = token.client_id

        if self._lang is not None:
            full_headers['X-Market'] = self._lang + '_' + self._country

        full_headers.update(self.BASE_HEADERS)
        return full_headers
