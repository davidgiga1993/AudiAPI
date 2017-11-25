from abc import abstractmethod


class ClimaRequestFactory:
    @abstractmethod
    def build(self):
        pass


class StartClimaRequestFactory(ClimaRequestFactory):
    SOURCE_AUX = 'auxiliary'
    SOURCE_AUTOMATIC = 'automatic'
    SOURCE_ELECTRIC = 'electric'

    def __init__(self, source: str):
        self.__source = source

    def build(self):
        return {
            'action': {
                'type': 'startClimatisation',
                'settings': {
                    'heaterSource': self.__source
                }
            }
        }


class StopClimaRequestFactory(ClimaRequestFactory):
    def build(self):
        return {
            'action': {
                'type': 'stopClimatisation'
            }
        }
