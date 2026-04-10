"""
Clinical Context Packager

Bundles FHIR R4 resources into typed ClinicalContextBundle instances
that agent frameworks can consume directly.

The context bundle is the core output of EHR-MCP:
any agent (LangChain, CrewAI, LangGraph, AutoGen) receives a
clean, typed, pre-packaged view of a patient's clinical state
without needing to understand FHIR internals or vendor quirks.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from ehr_mcp.fhir_client import FHIRClient
from ehr_mcp.schemas import (
    AllergyResource,
    ClinicalContextBundle,
    ConditionResource,
    DiagnosticReportResource,
    EncounterResource,
    FHIRResourceType,
    MedicationResource,
    ObservationResource,
    PatientContextRequest,
    PatientResource,
)

logger = logging.getLogger(__name__)


class ClinicalContextPackager:
    """
    Orchestrates FHIR resource retrieval and packages everything
    into a typed ClinicalContextBundle for agent consumption.
    """

    def __init__(self, fhir_client: Optional[FHIRClient] = None):
        self.client = fhir_client or FHIRClient()

    async def build_context(self, request: PatientContextRequest) -> ClinicalContextBundle:
        """Build a fully typed clinical context bundle for a patient."""
        logger.info(f"Building clinical context for patient {request.patient_id}")

        vendor = await self.client.detect_vendor()
        bundle = ClinicalContextBundle(
            patient_id=request.patient_id,
            vendor=vendor,
            bundle_generated_at=datetime.now(timezone.utc).isoformat(),
        )

        for resource_type in request.include_resources:
            try:
                if resource_type == FHIRResourceType.PATIENT:
                    raw = await self.client.get_patient(request.patient_id)
                    bundle.patient = PatientResource.from_fhir(raw)

                elif resource_type == FHIRResourceType.CONDITION:
                    raws = await self.client.get_conditions(request.patient_id)
                    bundle.conditions = [ConditionResource.from_fhir(r) for r in raws]

                elif resource_type == FHIRResourceType.MEDICATION_REQUEST:
                    raws = await self.client.get_medications(request.patient_id)
                    bundle.medications = [MedicationResource.from_fhir(r) for r in raws]

                elif resource_type == FHIRResourceType.ALLERGY_INTOLERANCE:
                    raws = await self.client.get_allergies(request.patient_id)
                    bundle.allergies = [AllergyResource.from_fhir(r) for r in raws]

                elif resource_type == FHIRResourceType.OBSERVATION:
                    raws = await self.client.get_observations(request.patient_id)
                    bundle.observations = [ObservationResource.from_fhir(r) for r in raws]

                elif resource_type == FHIRResourceType.ENCOUNTER:
                    raws = await self.client.get_encounters(request.patient_id)
                    bundle.encounters = [EncounterResource.from_fhir(r) for r in raws]

                elif resource_type == FHIRResourceType.DIAGNOSTIC_REPORT:
                    raws = await self.client.get_diagnostic_reports(request.patient_id)
                    bundle.diagnostic_reports = [DiagnosticReportResource.from_fhir(r) for r in raws]

            except Exception as e:
                logger.warning(
                    f"Failed to fetch {resource_type.value} "
                    f"for patient {request.patient_id}: {e}"
                )

        logger.info(
            f"Context bundle built — "
            f"{len(bundle.conditions)} conditions ({bundle.active_condition_count} active), "
            f"{len(bundle.medications)} medications ({bundle.active_medication_count} active), "
            f"{len(bundle.allergies)} allergies, "
            f"{len(bundle.observations)} observations"
        )
        return bundle

    def summarize(self, bundle: ClinicalContextBundle) -> str:
        """
        Produce a plain-language clinical summary string for direct
        injection into an agent's prompt or system message.

        Uses typed model attributes — no raw dict .get() chains.
        """
        lines = []

        if bundle.patient:
            p = bundle.patient
            lines.append(f"Patient: {p.display_name or 'Unknown'} (ID: {bundle.patient_id})")
            lines.append(f"DOB: {p.birth_date or 'Unknown'}")
            lines.append(f"Gender: {p.gender or 'Unknown'}")
            if p.race:
                lines.append(f"Race: {p.race}")
            if p.ethnicity:
                lines.append(f"Ethnicity: {p.ethnicity}")

        if bundle.conditions:
            active = [c for c in bundle.conditions if c.is_active]
            label = f"Active Conditions ({len(active)})" if active else f"Conditions ({len(bundle.conditions)})"
            lines.append(f"\n{label}:")
            display_list = active[:10] if active else bundle.conditions[:10]
            for c in display_list:
                icd = f" [{c.icd10_code}]" if c.icd10_code else ""
                lines.append(f"  - {c.display_text or 'Unknown condition'}{icd}")

        if bundle.medications:
            active_meds = [m for m in bundle.medications if m.status == "active"]
            label = f"Active Medications ({len(active_meds)})" if active_meds else f"Medications ({len(bundle.medications)})"
            lines.append(f"\n{label}:")
            display_list = active_meds[:10] if active_meds else bundle.medications[:10]
            for m in display_list:
                dosage = f" — {m.dosage_text}" if m.dosage_text else ""
                lines.append(f"  - {m.display_text or 'Unknown medication'}{dosage}")

        if bundle.allergies:
            lines.append(f"\nAllergies ({len(bundle.allergies)}):")
            for a in bundle.allergies[:10]:
                severity = f" [{a.highest_severity}]" if a.highest_severity else ""
                lines.append(f"  - {a.display_text or 'Unknown allergen'}{severity}")

        if bundle.observations:
            lines.append(f"\nRecent Observations ({len(bundle.observations)}):")
            for o in bundle.observations[:10]:
                value = f": {o.value_display}" if o.value_display else ""
                loinc = f" [LOINC {o.loinc_code}]" if o.loinc_code else ""
                lines.append(f"  - {o.display_text or 'Unknown'}{value}{loinc}")

        if bundle.encounters:
            lines.append(f"\nRecent Encounters ({len(bundle.encounters)}):")
            for e in bundle.encounters[:5]:
                date = f" on {e.period_start[:10]}" if e.period_start else ""
                enc_class = f" [{e.encounter_class_display}]" if e.encounter_class_display else ""
                lines.append(f"  - {e.display_text or 'Visit'}{enc_class}{date}")

        lines.append(f"\nEHR Vendor: {bundle.vendor or 'Unknown'}")
        lines.append(f"FHIR Version: {bundle.fhir_version}")
        if bundle.bundle_generated_at:
            lines.append(f"Bundle Generated: {bundle.bundle_generated_at}")

        return "\n".join(lines)
