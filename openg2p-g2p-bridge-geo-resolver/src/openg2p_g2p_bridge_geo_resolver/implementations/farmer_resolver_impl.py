import logging
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ..engine import get_engine
from ..interface.geo_resolver_interface import GeoResolver
from ..models import G2PFarmerRegistry

_logger = logging.getLogger("farmer_geo_resolver_impl")
_engine = get_engine()

session_maker = sessionmaker(bind=_engine.get("db_engine_registry"), expire_on_commit=False)


class FarmerGeoResolverImpl(GeoResolver):
    def resolve_geo(self, batch_beneficiary_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        with session_maker() as registry_session:
            _logger.info(f"Resolving geo for {len(batch_beneficiary_list)} beneficiaries")
            results = []

            beneficiary_ids = [item["beneficiary_id"] for item in batch_beneficiary_list]
            farmer_details = registry_session.execute(
                select(
                    G2PFarmerRegistry.link_registry_id,
                    G2PFarmerRegistry.large_area_id,
                    G2PFarmerRegistry.large_area_code,
                    G2PFarmerRegistry.small_area_id,
                    G2PFarmerRegistry.small_area_code,
                ).where(G2PFarmerRegistry.link_registry_id.in_(beneficiary_ids))
            ).fetchall()
            _logger.info(f"Fetched {len(farmer_details)} farmer details for the provided beneficiary IDs")
            if not farmer_details:
                _logger.warning(f"No farmer details found for the provided beneficiary IDs {beneficiary_ids}")
                return results
            farmer_map = {row.link_registry_id: row for row in farmer_details}
            for item in batch_beneficiary_list:
                row = farmer_map.get(item["beneficiary_id"])
                if row:
                    results.append(
                        {
                            "disbursement_id": item["disbursement_id"],
                            "beneficiary_id": item["beneficiary_id"],
                            "administrative_zone_id_large": row.large_area_id,
                            "administrative_zone_mnemonic_large": row.large_area_code,
                            "administrative_zone_id_small": row.small_area_id,
                            "administrative_zone_mnemonic_small": row.small_area_code,
                        }
                    )
            return results
