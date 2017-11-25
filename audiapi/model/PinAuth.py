class PinAuthInfoResponse:
    def __init__(self):
        self.security_token = ''
        self.pin_transmission = SecurityPinTransmission()


class SecurityPinTransmission:
    def __init__(self):
        self.challenge = ''
        self.hash_procedure_version = 0
        self.user_challenge = ''
