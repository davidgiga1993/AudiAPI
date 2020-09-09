from __future__ import annotations

import json
import os
import time
from typing import Dict, Optional


class Token:
    def __init__(self):
        self.access_token = ''
        self.token_type = ''
        self.refresh_token = ''
        self.id_token = ''
        self.scope = ''
        self.expires_in = 0
        self.client_id = None
        """
        The client ID is only used for certain endpoints
        """

    def valid(self) -> bool:
        """
        Checks if this token is still valid

        :return: True if valid
        """
        return self.expires_in > int(time.time())

    @staticmethod
    def parse(data, relative_timestamp=True):
        token = Token()
        token.access_token = data.get('access_token')
        token.token_type = data.get('token_type')
        token.refresh_token = data.get('refresh_token')
        token.id_token = data.get('id_token')
        token.scope = data.get('scope')
        raw_timestamp = data.get('expires_in')
        if relative_timestamp:
            raw_timestamp += int(time.time())
        token.expires_in = raw_timestamp
        return token

    def __str__(self):
        return 'Access token: ' + self.access_token


class TokenProvider:
    """
    Provides the correct access token depending on the required scope of the request
    """
    FILE = 'tokens.json'

    def __init__(self):
        self._scope_map = {}  # type: Dict[str, Token]
        """
        Maps each scope to the associated access token
        """

    def valid(self) -> bool:
        """
       Checks if all tokens are still valid

       :return: True if valid
       """
        for token in set(self._scope_map.values()):
            if not token.valid():
                return False
        return True

    def get_token(self, scope: str) -> Optional[Token]:
        if scope in self._scope_map:
            return self._scope_map[scope]

        # Use default token
        return self._scope_map.get(None)

    def add_token(self, token: Token):
        if token.scope is None:
            # Default token
            self._scope_map[None] = token
            return

        scopes = token.scope.split(' ')
        for scope in scopes:
            self._scope_map[scope] = token

    def persist(self):
        data = []
        for token in set(self._scope_map.values()):
            data.append(token.__dict__)

        with open(self.FILE, 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def load() -> Optional[TokenProvider]:
        if not os.path.isfile(TokenProvider.FILE):
            return None

        with open(TokenProvider.FILE) as data_file:
            data = json.load(data_file)

        provider = TokenProvider()
        for token_data in data:
            token = Token.parse(token_data, relative_timestamp=False)
            provider.add_token(token)
        return provider
