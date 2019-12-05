class BatteryChargeResponse:
    """
    Represents a battery charge response
    """

    def parse(self, data):
        self.charger = data.get('charger')

    def __str__(self):
        return str(self.__dict__)
