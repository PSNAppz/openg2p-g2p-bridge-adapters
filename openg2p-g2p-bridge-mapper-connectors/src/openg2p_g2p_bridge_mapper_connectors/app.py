# ruff: noqa: E402


from openg2p_fastapi_common.app import Initializer as BaseInitializer
from openg2p_fastapi_common.utils.crypto import KeymanagerCryptoHelper
from openg2p_fastapi_partner_auth.jwt_validation_helper import JWTValidationHelper

from .client import SPARMapperV1Client
from .factory import MapperFactory
from .implementations import SPARMapperV1


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        MapperFactory()
        SPARMapperV1Client()
        SPARMapperV1()
        JWTValidationHelper()
        KeymanagerCryptoHelper()
