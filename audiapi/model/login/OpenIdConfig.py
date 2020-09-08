from typing import List


class OpenIdConfig:
    def __init__(self):
        self.authorization_endpoint = ''  # type: str
        self.token_endpoint = ''  # type: str
        self.revocation_endpoint = ''  # type: str
        self.end_session_endpoint = ''  # type: str
        self.jwks_uri = ''  # type: str
        self.userinfo_endpoint = ''  # type: str
        self.response_types_supported = []  # type: List[str]
        self.subject_types_supported = []  # type: List[str]
        self.id_token_signing_alg_values_supported = []  # type: List[str]
        self.code_challenge_methods_supported = []  # type: List[str]
        self.scopes_supported = []  # type: List[str]
        self.claims_supported = []  # type: List[str]
        self.grant_types_supported = []  # type: List[str]
        self.ui_locales_supported = []  # type: List[str]
        self.token_endpoint_auth_methods_supported = []  # type: List[str]
