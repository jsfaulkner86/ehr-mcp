"""
FHIR R4 Client — Vendor-Agnostic Abstraction Layer

Abstracts FHIR R4 resource access behind a clean interface.
Works with any conformant FHIR R4 server:
  - Epic FHIR (R4)
  - Oracle Health (Cerner) FHIR
  - Meditech Expanse FHIR
  - Azure Health Data Services
  - AWS HealthLake
  - HAPI FHIR (open source)

Authentication is handled by SMARTBackendAuth.
"""

import os
import logging
from typing import Optional

import httpx

from ehr_mcp.auth import SMARTBackendAuth
from ehr_mcp.schemas import FHIRResourceType, ResourceSearchParams

logger = logging.getLogger(__name__)


class FHIRClient:
    """
    FHIR R4 REST client with SMART backend services auth.
    Vendor-agnostic — configure via FHIR_BASE_URL environment variable.
    """

    def __init__(
        self,
        fhir_base_url: Optional[str] = None,
        auth: Optional[SMARTBackendAuth] = None,
    ):
        self.fhir_base_url = (fhir_base_url or os.getenv("FHIR_BASE_URL", "")).rstrip("/")
        self.auth = auth or SMARTBackendAuth()
        self._vendor: Optional[str] = None

    async def _get_headers(self) -> dict:
        token = await self.auth.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        }

    async def detect_vendor(self) -> str:
        """
        Probe the FHIR capability statement to detect EHR vendor.
        Useful for logging, telemetry, and vendor-specific workarounds.
        """
        if self._vendor:
            return self._vendor

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.fhir_base_url}/metadata",
                    headers={"Accept": "application/fhir+json"},
                    timeout=10,
                )
                if response.status_code == 200:
                    meta = response.json()
                    publisher = meta.get("publisher", "").lower()
                    software = meta.get("software", {}).get("name", "").lower()
                    combined = publisher + software

                    if "epic" in combined:
                        self._vendor = "Epic"
                    elif "cerner" in combined or "oracle" in combined:
                        self._vendor = "Oracle Health (Cerner)"
                    elif "meditech" in combined:
                        self._vendor = "Meditech"
                    elif "hapi" in combined:
                        self._vendor = "HAPI FHIR"
                    else:
                        self._vendor = "Unknown FHIR R4 Server"
        except Exception as e:
            logger.warning(f"Vendor detection failed: {e}")
            self._vendor = "Unknown"

        logger.info(f"EHR vendor detected: {self._vendor}")
        return self._vendor

    async def get_resource(self, resource_type: str, resource_id: str) -> dict:
        """Fetch a single FHIR resource by type and ID."""
        url = f"{self.fhir_base_url}/{resource_type}/{resource_id}"
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()

    async def search_resources(self, params: ResourceSearchParams) -> list:
        """Search FHIR resources with standard search parameters."""
        search_params = {"_count": str(params.count)}

        if params.patient_id:
            search_params["patient"] = params.patient_id
        if params.encounter_id:
            search_params["encounter"] = params.encounter_id
        if params.additional_params:
            search_params.update(params.additional_params)

        url = f"{self.fhir_base_url}/{params.resource_type.value}"
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=search_params, timeout=30)
            response.raise_for_status()
            bundle = response.json()

        entries = bundle.get("entry", [])
        return [e["resource"] for e in entries if "resource" in e]

    async def get_patient(self, patient_id: str) -> dict:
        return await self.get_resource("Patient", patient_id)

    async def get_conditions(self, patient_id: str, count: int = 20) -> list:
        return await self.search_resources(ResourceSearchParams(
            resource_type=FHIRResourceType.CONDITION,
            patient_id=patient_id,
            count=count,
        ))

    async def get_medications(self, patient_id: str, count: int = 20) -> list:
        return await self.search_resources(ResourceSearchParams(
            resource_type=FHIRResourceType.MEDICATION_REQUEST,
            patient_id=patient_id,
            count=count,
        ))

    async def get_observations(self, patient_id: str, count: int = 20) -> list:
        return await self.search_resources(ResourceSearchParams(
            resource_type=FHIRResourceType.OBSERVATION,
            patient_id=patient_id,
            count=count,
        ))

    async def get_allergies(self, patient_id: str, count: int = 20) -> list:
        return await self.search_resources(ResourceSearchParams(
            resource_type=FHIRResourceType.ALLERGY_INTOLERANCE,
            patient_id=patient_id,
            count=count,
        ))

    async def get_encounters(self, patient_id: str, count: int = 10) -> list:
        return await self.search_resources(ResourceSearchParams(
            resource_type=FHIRResourceType.ENCOUNTER,
            patient_id=patient_id,
            count=count,
        ))

    async def get_diagnostic_reports(self, patient_id: str, count: int = 10) -> list:
        return await self.search_resources(ResourceSearchParams(
            resource_type=FHIRResourceType.DIAGNOSTIC_REPORT,
            patient_id=patient_id,
            count=count,
        ))
