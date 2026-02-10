from datetime import datetime
from enum import Enum
from typing import List, Optional

from openg2p_g2pconnect_common_lib.schemas import Request, StatusEnum, SyncResponse
from pydantic import BaseModel


class ResolveScope(Enum):
    yes_no = "yes_no"
    details = "details"


class ResolveStatusReasonCode(Enum):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_id_invalid = "rjct.id.invalid"
    rjct_fa_invalid = "rjct.fa.invalid"
    rjct_resolve_type_not_supported = "rjct.resolve_type.not_supported"
    succ_fa_active = "succ.fa.active"
    succ_fa_inactive = "succ.fa.inactive"
    succ_fa_not_found = "succ.fa.not_found"
    succ_fa_not_linked_to_id = "succ.fa.not_linked_to_id"
    succ_id_active = "succ.id.active"
    succ_id_inactive = "succ.id.inactive"
    succ_id_not_found = "succ.id.not_found"


class SingleResolveRequest(BaseModel):
    reference_id: str
    timestamp: str
    fa: Optional[str] = ""
    id: Optional[str] = ""
    name: Optional[str] = None
    scope: Optional[ResolveScope] = ResolveScope.yes_no
    additional_info: Optional[List[object]] = None
    locale: Optional[str] = "en"


class ResolveRequestMessage(BaseModel):
    transaction_id: str
    resolve_request: List[SingleResolveRequest]


class AccountProviderInfo(BaseModel):
    name: str
    code: str
    subcode: Optional[str]
    additional_info: Optional[List[object]] = None


class SingleResolveResponse(BaseModel):
    reference_id: str
    timestamp: datetime
    fa: Optional[str] = None
    id: Optional[str] = None
    account_provider_info: Optional[AccountProviderInfo] = None
    status: StatusEnum
    status_reason_code: Optional[ResolveStatusReasonCode] = None
    status_reason_message: Optional[str] = ""
    additional_info: Optional[List[object]] = None
    locale: Optional[str] = "en"


class ResolveResponseMessage(BaseModel):
    transaction_id: Optional[str] = None
    correlation_id: Optional[str] = ""
    resolve_response: List[SingleResolveResponse]


class ResolveRequest(Request):
    message: ResolveRequestMessage


class ResolveResponse(SyncResponse):
    message: ResolveResponseMessage
