from openg2p_fastapi_common.service import BaseService

from ..implementations.spar_mapper_v1 import SPARMapperV1
from ..interface.mapper_interface import MapperInterface


class MapperFactory(BaseService):
    @staticmethod
    def get_mapper() -> MapperInterface:
        return SPARMapperV1.get_component()
