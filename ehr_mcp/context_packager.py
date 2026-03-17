"""
Clinical Context Packager

Bundles FHIR R4 resources into structured context objects
that agent frameworks can consume directly.

The context bundle is the core output of EHR-MCP —
it gives any agent (LangChain, CrewAI, LangGraph, AutoGen)
a clean, pre-packaged view of a patient's clinical state
without the agent needing to understand FHIR internals.
"""

import logging
from typing import Optional

from ehr_mcp.fhir_client import FHIRClient
from ehr_mcp.schemas import PatientContextRequest, ClinicalContextBundle, FHIRResourceType

logger = logging.getLogger(__name__)


class ClinicalContextPackager:
    """
    Orchestrates FHIR resource retrieval and packages
    everything into a ClinicalContextBundle for agent consumption.
    """

    def __init__(self, fhir_client: Optional[FHIRClient] = None):
        self.client = fhir_client or FHIRClient()

    async def build_context(self, request: PatientContextRequest) -> ClinicalContextBundle:
        """Build a full clinical context bundle for a patient."""
        logger.info(f"Building clinical context for patient {request.patient_id}")

        vendor = await self.client.detect_vendor()
        bundle = ClinicalContextBundle(
            patient_id=request.patient_id,
            vendor=vendor,
        )

        for resource_type in request.include_resources:
            try:
                if resource_type == FHIRResourceType.PATIENT:
                    bundle.patient = await self.client.get_patient(request.patient_id)

                elif resource_type == FHIRResourceType.CONDITION:
                    bundle.conditions = await self.client.get_conditions(request.patient_id)

                elif resource_type == FHIRResourceType.MEDICATION_REQUEST:
                    bundle.medications = await self.client.get_medications(request.patient_id)

                elif resource_type == FHIRResourceType.ALLERGY_INTOLERANCE:
                    bundle.allergies = await self.client.get_allergies(request.patient_id)

                elif resource_type == FHIRResourceType.OBSERVATION:
                    bundle.observations = await self.client.get_observations(request.patient_id)

                elif resource_type == FHIRResourceType.ENCOUNTER:
                    bundle.encounters = await self.client.get_encounters(request.patient_id)

                elif resource_type == FHIRResourceType.DIAGNOSTIC_REPORT:
                    bundle.diagnostic_reports = await self.client.get_diagnostic_reports(request.patient_id)

            except Exception as e:
                logger.warning(f"Failed to fetch {resource_type.value} for patient {request.patient_id}: {e}")

        logger.info(
            f"Context bundle built — "
            f"{len(bundle.conditions)} conditions, "
            f"{len(bundle.medications)} medications, "
            f"{len(bundle.allergies)} allergies, "
            f"{len(bundle.observations)} observations"
        )
        return bundle

    def summarize(self, bundle: ClinicalContextBundle) -> str:
        """
        Produce a plain-language clinical summary string for direct
        injection into an agent's prompt or system message.
        """
        lines = []

        if bundle.patient:
            name = bundle.patient.get("name", [{}])
            display_name = "Unknown"
            if name:
                given = " ".join(name[0].get("given", []))
                family = name[0].get("family", "")
                display_name = f"{given} {family}".strip()
            lines.append(f"Patient: {display_name} (ID: {bundle.patient_id})")
            lines.append(f"DOB: {bundle.patient.get('birthDate', 'Unknown')}")
            lines.append(f"Gender: {bundle.patient.get('gender', 'Unknown')}")

        if bundle.conditions:
            lines.append(f"\nActive Conditions ({len(bundle.conditions)}):")
            for c in bundle.conditions[:10]:
                code = c.get("code", {}).get("text", "Unknown condition")
                lines.append(f"  - {code}")

        if bundle.medications:
            lines.append(f"\nMedications ({len(bundle.medications)}):")
            for m in bundle.medications[:10]:
                med = m.get("medicationCodeableConcept", {}).get("text", "Unknown medication")
                lines.append(f"  - {med}")

        if bundle.allergies:
            lines.append(f"\nAllergies ({len(bundle.allergies)}):")
            for a in bundle.allergies[:10]:
                substance = a.get("code", {}).get("text", "Unknown allergen")
                lines.append(f"  - {substance}")

        lines.append(f"\nEHR Vendor: {bundle.vendor or 'Unknown'}")
        lines.append(f"FHIR Version: {bundle.fhir_version}")

        return "\n".join(lines)
