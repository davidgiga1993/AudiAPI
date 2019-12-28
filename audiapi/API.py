import json
from json import JSONDecodeError

import requests

from audiapi.Token import Token


class API:
    """
    Wrapper for the audi API
    """
    BASE_URL = 'https://msg.audi.de/fs-car'
    BASE_CAR_URL = 'https://msg.audi.de/fs-car/bs/cf/v1/Audi/DE/vehicles'

    BASE_HEADERS = {'Accept': 'application/json',
                    'X-App-ID': 'de.audi.mmiapp',
                    'X-App-Name': 'MMIconnect',
                    'X-App-Version': '2.8.3',
                    'X-Brand': 'audi',
                    'X-Country-Id': 'DE',
                    'X-Language-Id': 'de',
                    'X-Platform': 'google',
                    'User-Agent': 'okhttp/2.7.4',
                    'ADRUM_1': 'isModule:true',
                    'ADRUM': 'isAray:true'}

    def __init__(self, proxy=None):
        """
        Creates a new API

        :param proxy: Proxy which should be used in the URL format e.g. http://proxy:8080
        """
        self.__token = None
        if proxy is not None:
            self.__proxy = {'http': proxy,
                            'https': proxy}
        else:
            self.__proxy = None

        self._lang = None
        self._country = None

    def set_market(self, country: str, language: str):
        """
        Sets the market area that should be used
        :param country: country (e.g. DE)
        :param language: Language (e.g. de)
        """
        self._lang = language
        self._country = country

    def use_token(self, token: Token):
        """
        Uses the given token for auth

        :param token: Token
        """
        self.__token = token

    def get(self, url):
        r = requests.get(url, headers=self._get_headers(), proxies=self.__proxy)
        return self._handle_response(r)

    def put(self, url, data=None, headers=None):
        full_headers = self._get_headers()
        full_headers.update(headers)
        r = requests.put(url, data, headers=full_headers, proxies=self.__proxy)
        return self._handle_response(r)

    def post(self, url, data=None, use_json: bool = True):
        if use_json and data is not None:
            data = json.dumps(data)
        r = requests.post(url, data=data, headers=self._get_headers(), proxies=self.__proxy)
        return self._handle_response(r)

    @staticmethod
    def _handle_response(response):
        if response.status_code == 404:
            raise Exception('Unknown endpoint - 404')
        try:
            data = response.json()
        except JSONDecodeError:
            print('Error while decoding response: ' + str(response.text))
            raise

        error = data.get('error')
        if error is not None:
            error_msg = error.get('description', '')
            raise Exception('API error: ' + str(error) + '\n' + error_msg)
        return data

    def _get_headers(self):
        full_headers = dict()
        token_value = 'AudiAuth'
        if self.__token is not None:
            token_value = 'Bearer ' + self.__token.access_token
        full_headers['Authorization'] = token_value

        if self._lang is not None:
            full_headers['X-Market'] = self._lang + '_' + self._country

        full_headers.update(self.BASE_HEADERS)
        return full_headers
