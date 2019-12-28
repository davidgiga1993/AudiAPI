from Token import Token
from model.UserInfo import UserInfo
from services.Service import Service


class LogonService(Service):
    """
    General API logon service
    (Audi ID)
    """

    def login(self, user: str, password: str, persist_token: bool = True):
        """
        Creates a new session using the given credentials

        :param user: User
        :param password: Password
        :param persist_token: True if the token should be persisted in the file system after login
        """
        token = self.__login_request(user, password)
        self._api.use_token(token)
        if persist_token:
            token.persist()

    def get_user_info(self):
        """
        Returns information about the current user
        :return: User information
        :rtype: UserInfo
        """
        reply = self._api.get(self.url('/v1/userinfo'))
        return self._to_dto(reply, UserInfo())

    def restore_token(self):
        """
        Tries to restore the latest persisted auth token

        :return: True if token could be restored
        :rtype: bool
        """
        token = Token.load()
        if token is None or not token.valid():
            return False
        self._api.use_token(token)
        return True

    def __login_request(self, user: str, password: str):
        """
        Requests a login token for the given user

        :param user: User
        :param password: Password
        :return: Token
        :rtype: Token
        """
        data = {'grant_type': 'password',
                'scope': 'openid profile email mbb offline_access mbbuserid myaudi selfservice:read selfservice:write',
                'response_type': 'token id_token',
                'client_id': 'mmiconnect_android',
                'username': user,
                'password': password}

        reply = self._api.post(self.url('/v1/token'), data=data, use_json=False)
        return Token.parse(reply)

    def _get_path(self):
        return 'https://id.audi.com'


class MarketsService(Service):
    def _get_path(self):
        return None

    def get_markets(self):
        """
        Returns all available countries and their languages

        :return: List of markets
        :rtype: dict(str, object)
        """
        markets = self._api.get('https://apps.audi.com/onetouch/configs/markets.json')
        return markets['countries']['countrySpecifications']
