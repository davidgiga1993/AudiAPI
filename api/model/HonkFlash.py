class HonkFlashAction:
    def __init__(self, data):
        request = data.get('honkAndFlashRequest')
        self.id = request.get('id')
        self.last_updated = request.get('lastUpdated')
        self.duration = request.get('serviceDuration')
        self.operation = request.get('serviceOperationCode')
        self.user_pos = request.get('userPosition')


class RemoteHonkFlashActionStatus:
    def __init__(self, data):
        request = data.get('status')
        self.status = request.get('statusCode')
        self.reason = request.get('statusReason')
