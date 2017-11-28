class CurrentVehicleDataResponse:
    def __init__(self, data):
        data = data['CurrentVehicleDataResponse']
        self.request_id = data['requestId']
        self.vin = data['vin']
