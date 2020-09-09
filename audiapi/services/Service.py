from abc import ABCMeta, abstractmethod

from API import API


class Service(metaclass=ABCMeta):

    def __init__(self, api: API):
        self._api = api
        """
        API for communicating

        :type _api: API
        """

    def get(self, path: str, scope: str = None, **format_data):
        if scope is None:
            scope = self._get_scope()
        return self._api.get(self.url(path, **format_data), scope=scope)

    def post(self, path: str, scope: str = None, data=None, **format_data):
        if scope is None:
            scope = self._get_scope()
        return self._api.post(self.url(path, **format_data), scope=scope, data=data)

    def url(self, part, **format_data):
        """
        Builds a full URL using the given parts

        :param part URL part which should be added at the end
        :param format_data: Format arguments
        :return: URL
        :rtype: str
        """
        url = self._get_path() + part
        return url.format(**format_data)

    def _to_dto(self, reply: dict, dto_obj: object):
        """
        Sets the fields in the given DTO object using the given dict

        :param reply: JSON decoded reply as dict
        :param dto_obj: DTO object
        :return: Same object
        """
        dto_obj.__dict__.update(reply)
        return dto_obj

    @abstractmethod
    def _get_path(self):
        """
        Returns the url path for this service

        :return: URL path
        :rtype: str
        """
        pass

    @abstractmethod
    def _get_scope(self) -> str:
        """
        Returns the default token scope required by this service to execute a request
        :return: Token scope
        """


class MsgService(Service, metaclass=ABCMeta):
    def _get_path(self):
        return 'https://msg.audi.de'


class MbbService(MsgService):
    def __init__(self, api: API, brand: str, country: str):
        super().__init__(api)
        self._brand = brand
        self._country = country

    def url(self, part, **format_data):
        return super().url(part, **format_data, brand=self._brand, country=self._country)

    def _get_scope(self) -> str:
        return 'vehicle'


class MbbMalService(Service):
    def _get_path(self):
        return 'https://mal-1a.prd.ece.vwg-connect.com/api'

    def _get_scope(self) -> str:
        return 'fal'
