class RequestStatus:
    IN_PROGRESS = 'request_in_progress'
    SUCCESS = 'request_successful'
    FAIL = 'request_fail'

    def __init__(self, data):
        data = data['requestStatusResponse']
        self.status = data['status']
        self.vin = data['vin']
