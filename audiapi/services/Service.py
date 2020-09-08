from abc import ABCMeta, abstractmethod

from API import API


class Service(metaclass=ABCMeta):
    COMPANY = 'Audi'
    COUNTRY = 'DE'

    def __init__(self, api: API):
        self._api = api
        """
        API for communicating

        :type _api: API
        """

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


class MsgService(Service):
    def _get_path(self):
        return 'https://msg.audi.de'
