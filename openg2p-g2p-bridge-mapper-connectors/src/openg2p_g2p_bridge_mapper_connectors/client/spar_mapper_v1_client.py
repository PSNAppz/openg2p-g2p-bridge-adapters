import logging
from functools import cached_property

import httpx
import orjson
from openg2p_fastapi_common.errors.base_exception import BaseAppException
from openg2p_fastapi_common.service import BaseService
from openg2p_fastapi_common.utils.crypto import CryptoHelper

from ..config import Settings
from ..schemas.spar_resolve_v1_schema import ResolveRequest, ResolveResponse

_config = Settings.get_config()
_logger = logging.getLogger("spar_mapper_v1_client")


class SPARMapperV1Client(BaseService):
    """Client for making requests to SPAR Mapper API (V1 G2P Connect structure)."""

    def __init__(self):
        super().__init__()
        self.url = _config.spar_mapper_url
        self.api_sign_enabled = _config.spar_mapper_api_sign_enabled
        self.api_sign_crypto_helper_name = "spar_mapper_crypto"
        self.timeout = 30.0

    @cached_property
    def crypto_helper(self):
        """Get the CryptoHelper component for JWT signing."""
        return CryptoHelper.get_component(name=self.api_sign_crypto_helper_name)

    async def resolve_request(self, request: ResolveRequest, headers: dict | None = None) -> ResolveResponse:
        """
        Send a resolve request to the SPAR Mapper API.

        Args:
            request: ResolveRequest object containing the request data
            headers: Optional additional headers to include in the request

        Returns:
            ResolveResponse object containing the response data

        Raises:
            BaseAppException: If the request fails
        """
        try:
            payload = request.model_dump(mode="json")

            orig_headers = {"content-type": "application/json"}

            # Add JWT signature if API signing is enabled
            if self.api_sign_enabled:
                _logger.debug("Creating JWT signature for request")
                # orig_headers["Signature"] = await self.crypto_helper.create_jwt_token(payload)

            if headers:
                orig_headers.update(headers)

            _logger.info(f"Sending resolve request to {self.url}")
            _logger.debug(f"Request payload: {payload}")

            # Create client per-request to avoid event loop issues with Celery fork workers
            async with httpx.AsyncClient(timeout=self.timeout) as http_client:
                res = await http_client.post(
                    self.url,
                    content=orjson.dumps(payload, option=orjson.OPT_SORT_KEYS),
                    headers=orig_headers,
                )
                _logger.info(f"Response data: {res.text}")
                res.raise_for_status()

                response_data = res.json()

            _logger.info("Resolve request completed successfully")

            # Parse and validate the response
            resolve_response = ResolveResponse.model_validate(response_data)

            # Log response details
            _logger.info(
                f"Transaction ID: {resolve_response.message.transaction_id}, "
                f"Resolve responses count: {len(resolve_response.message.resolve_response)}"
            )

            return resolve_response

        except httpx.HTTPStatusError as e:
            _logger.exception("HTTP Error in resolve request")
            raise BaseAppException(
                message="Error in resolve request",
                code=str(e.response.status_code),
            ) from e
        except Exception as e:
            _logger.exception("Unknown Error in resolve request")
            raise BaseAppException(
                message="Unknown Error in resolve request",
                code="500",
            ) from e
