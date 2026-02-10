import logging
from datetime import datetime

from ..client import SPARMapperV1Client
from ..interface.mapper_interface import MapperInterface
from ..schemas import ResolveRequest, ResolveResponse, ResolveResult
from ..schemas.spar_resolve_v1_schema import (
    ResolveRequest as SparResolveRequest,
)
from ..schemas.spar_resolve_v1_schema import (
    ResolveRequestMessage,
    ResolveScope,
    SingleResolveRequest,
)
from ..schemas.spar_resolve_v1_schema import (
    ResolveResponse as SparResolveResponse,
)

_logger = logging.getLogger("spar_mapper_v1_impl")


class SPARMapperV1(MapperInterface):
    def __init__(self):
        super().__init__()
        self.client = SPARMapperV1Client.get_component()

    async def resolve(self, resolve_request: ResolveRequest) -> ResolveResponse | None:
        """
        Resolve the given request from SPAR Mapper and return the result.

        Args:
            resolve_request: ResolveRequest object containing beneficiary_ids

        Returns:
            ResolveResponse object with a list of results (id, fa, name)
            or None if the request fails
        """
        _logger.info(f"Received resolve request with {len(resolve_request.beneficiary_ids)} disbursement IDs")
        _logger.info(f"Disbursement IDs: {resolve_request.beneficiary_ids}")

        try:
            # Convert custom ResolveRequest to SPAR ResolveRequest
            spar_request = self._convert_to_spar_request(resolve_request)

            _logger.info(
                f"Converted to SPAR request with transaction_id: {spar_request.message.transaction_id}"
            )

            # Await the async resolve_request in an async context
            spar_resolve_response: SparResolveResponse = await self.client.resolve_request(spar_request)

            _logger.info("Resolve request completed successfully")
            _logger.info(
                f"Transaction ID: {spar_resolve_response.message.transaction_id}, "
                f"Response: {spar_resolve_response}"
            )

            # Convert SPAR ResolveResponse to custom ResolveResponse
            resolve_response = self._convert_from_spar_response(spar_resolve_response)

            _logger.info(f"Returning {len(resolve_response.results)} resolve results")
            return resolve_response

        except Exception as e:
            _logger.error(f"Failed to resolve the request: {e}", exc_info=True)
            return None

    def _convert_to_spar_request(self, resolve_request: ResolveRequest) -> SparResolveRequest:
        """
        Convert custom ResolveRequest to SPAR ResolveRequest.

        Args:
            resolve_request: Custom ResolveRequest with beneficiary_ids

        Returns:
            SparResolveRequest with G2P Connect structure
        """
        # Create SingleResolveRequest for each disbursement ID
        single_resolve_requests = [
            SingleResolveRequest(
                reference_id=disbursement_id,
                timestamp=datetime.now().isoformat(),
                id=disbursement_id,
                fa="",
                scope=ResolveScope.details,
                locale="en",
            )
            for disbursement_id in resolve_request.beneficiary_ids
        ]

        # Create the full SPAR request with flatter message structure
        spar_request = SparResolveRequest(
            message=ResolveRequestMessage(
                transaction_id=f"txn_{int(datetime.now().timestamp())}",
                resolve_request=single_resolve_requests,
            )
        )

        return spar_request

    def _convert_from_spar_response(self, spar_response: SparResolveResponse) -> ResolveResponse:
        """
        Convert SPAR ResolveResponse to custom ResolveResponse.

        Args:
            spar_response: SPAR ResolveResponse with G2P Connect structure

        Returns:
            ResolveResponse object with a list of results
        """
        results = []

        for single_response in spar_response.message.resolve_response:
            id_value = single_response.id

            fa_value = single_response.fa

            name_value = (
                single_response.account_provider_info.name if single_response.account_provider_info else None
            )

            result = ResolveResult(
                id=id_value,
                fa=fa_value,
                name=name_value,
            )

            results.append(result)

            _logger.debug(
                f"Converted result: id={id_value}, fa={fa_value}, name={name_value}, "
                f"status={single_response.status}, status_reason={single_response.status_reason_code}"
            )

        return ResolveResponse(results=results)
