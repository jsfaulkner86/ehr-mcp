"""
Tests for ehr_mcp/schemas.py — Pydantic v2 data contracts.

Focuses on:
- from_fhir() factory method correctness
- display_text resolution logic
- Derived field computation (icd10_code, rxnorm_code, loinc_code)
- ClinicalContextBundle active count computation
- All fields Optional — no raises on sparse FHIR resources
"""

import pytest
from ehr_mcp.schemas import (
    ClinicalContextBundle,
    ConditionResource,
    MedicationResource,
    AllergyResource,
    ObservationResource,
    EncounterResource,
    PatientResource,
    CodeableConcept,
    HumanName,
    FHIRResourceType,
    MCPToolResult,
    PatientContextRequest,
)


# ---------------------------------------------------------------------------
# CodeableConcept
# ---------------------------------------------------------------------------

class TestCodeableConcept:
    def test_resolves_display_from_text(self):
        cc = CodeableConcept(text="Hypertension")
        assert cc.display_text == "Hypertension"

    def test_resolves_display_from_coding_display(self):
        from ehr_mcp.schemas import CodingEntry
        cc = CodeableConcept(coding=[CodingEntry(display="Gestational Hypertension")])
        assert cc.display_text == "Gestational Hypertension"

    def test_resolves_display_from_coding_code_fallback(self):
        from ehr_mcp.schemas import CodingEntry
        cc = CodeableConcept(coding=[CodingEntry(code="O13")])
        assert cc.display_text == "O13"

    def test_empty_codeable_concept_no_raise(self):
        cc = CodeableConcept()
        assert cc.display_text is None


# ---------------------------------------------------------------------------
# HumanName
# ---------------------------------------------------------------------------

class TestHumanName:
    def test_display_name_from_text(self):
        hn = HumanName(text="Maria Johnson")
        assert hn.display_name == "Maria Johnson"

    def test_display_name_assembled_from_parts(self):
        hn = HumanName(family="Johnson", given=["Maria"])
        assert hn.display_name == "Maria Johnson"

    def test_display_name_with_prefix(self):
        hn = HumanName(prefix=["Dr."], given=["Sarah"], family="Chen")
        assert hn.display_name == "Dr. Sarah Chen"


# ---------------------------------------------------------------------------
# PatientResource
# ---------------------------------------------------------------------------

class TestPatientResource:
    def test_from_fhir_basic(self, fhir_patient):
        patient = PatientResource.from_fhir(fhir_patient)
        assert patient.id == "test-patient-001"
        assert patient.birth_date == "1985-03-14"
        assert patient.gender == "female"

    def test_display_name_resolved(self, fhir_patient):
        patient = PatientResource.from_fhir(fhir_patient)
        assert patient.display_name == "Maria Johnson"

    def test_us_core_race_extension(self):
        raw = {
            "resourceType": "Patient",
            "id": "pt-race",
            "extension": [{
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                "extension": [{"url": "text", "valueString": "Black or African American"}]
            }]
        }
        patient = PatientResource.from_fhir(raw)
        assert patient.race == "Black or African American"

    def test_sparse_patient_no_raise(self):
        patient = PatientResource.from_fhir({"resourceType": "Patient", "id": "sparse"})
        assert patient.id == "sparse"
        assert patient.display_name is None


# ---------------------------------------------------------------------------
# ConditionResource
# ---------------------------------------------------------------------------

class TestConditionResource:
    def test_icd10_code_extracted(self, fhir_condition_active):
        condition = ConditionResource.from_fhir(fhir_condition_active)
        assert condition.icd10_code == "O14.10"

    def test_display_text_resolved(self, fhir_condition_active):
        condition = ConditionResource.from_fhir(fhir_condition_active)
        assert condition.display_text == "Pre-eclampsia"

    def test_is_active_resolved(self, fhir_condition_active):
        condition = ConditionResource.from_fhir(fhir_condition_active)
        assert condition.is_active is True

    def test_subject_id_extracted(self, fhir_condition_active):
        condition = ConditionResource.from_fhir(fhir_condition_active)
        assert condition.subject_id == "test-patient-001"

    def test_inactive_condition(self):
        raw = {
            "resourceType": "Condition",
            "id": "cond-inactive",
            "clinicalStatus": {
                "coding": [{"code": "resolved"}]
            },
            "code": {"text": "UTI"},
        }
        condition = ConditionResource.from_fhir(raw)
        assert condition.is_active is False


# ---------------------------------------------------------------------------
# MedicationResource
# ---------------------------------------------------------------------------

class TestMedicationResource:
    def test_rxnorm_code_extracted(self, fhir_medication_active):
        med = MedicationResource.from_fhir(fhir_medication_active)
        assert med.rxnorm_code == "1049502"

    def test_display_text_resolved(self, fhir_medication_active):
        med = MedicationResource.from_fhir(fhir_medication_active)
        assert med.display_text == "Labetalol 200 MG Oral Tablet"

    def test_dosage_text_resolved(self, fhir_medication_active):
        med = MedicationResource.from_fhir(fhir_medication_active)
        assert med.dosage_text == "200mg twice daily"

    def test_status_active(self, fhir_medication_active):
        med = MedicationResource.from_fhir(fhir_medication_active)
        assert med.status == "active"


# ---------------------------------------------------------------------------
# AllergyResource
# ---------------------------------------------------------------------------

class TestAllergyResource:
    def test_display_text_resolved(self, fhir_allergy):
        allergy = AllergyResource.from_fhir(fhir_allergy)
        assert allergy.display_text == "Penicillin"

    def test_criticality(self, fhir_allergy):
        allergy = AllergyResource.from_fhir(fhir_allergy)
        assert allergy.criticality == "high"

    def test_subject_id_extracted(self, fhir_allergy):
        allergy = AllergyResource.from_fhir(fhir_allergy)
        assert allergy.subject_id == "test-patient-001"


# ---------------------------------------------------------------------------
# ObservationResource
# ---------------------------------------------------------------------------

class TestObservationResource:
    def test_loinc_code_extracted(self, fhir_observation_lab):
        obs = ObservationResource.from_fhir(fhir_observation_lab)
        assert obs.loinc_code == "2857-1"

    def test_value_display_resolved(self, fhir_observation_lab):
        obs = ObservationResource.from_fhir(fhir_observation_lab)
        assert obs.value_display == "11.2 g/dL"

    def test_observation_category_resolved(self, fhir_observation_lab):
        obs = ObservationResource.from_fhir(fhir_observation_lab)
        assert obs.observation_category == "laboratory"

    def test_subject_id_extracted(self, fhir_observation_lab):
        obs = ObservationResource.from_fhir(fhir_observation_lab)
        assert obs.subject_id == "test-patient-001"


# ---------------------------------------------------------------------------
# EncounterResource
# ---------------------------------------------------------------------------

class TestEncounterResource:
    def test_period_resolved(self, fhir_encounter):
        enc = EncounterResource.from_fhir(fhir_encounter)
        assert enc.period_start == "2026-01-15T10:00:00Z"
        assert enc.period_end == "2026-01-15T10:45:00Z"

    def test_encounter_class_display(self, fhir_encounter):
        enc = EncounterResource.from_fhir(fhir_encounter)
        assert enc.encounter_class_display == "Ambulatory"

    def test_service_provider_resolved(self, fhir_encounter):
        enc = EncounterResource.from_fhir(fhir_encounter)
        assert enc.service_provider_display == "Metro Women's Health"


# ---------------------------------------------------------------------------
# ClinicalContextBundle
# ---------------------------------------------------------------------------

class TestClinicalContextBundle:
    def test_active_condition_count(self, fhir_condition_active):
        condition = ConditionResource.from_fhir(fhir_condition_active)
        bundle = ClinicalContextBundle(
            patient_id="test-patient-001",
            conditions=[condition]
        )
        assert bundle.active_condition_count == 1

    def test_active_medication_count(self, fhir_medication_active):
        med = MedicationResource.from_fhir(fhir_medication_active)
        bundle = ClinicalContextBundle(
            patient_id="test-patient-001",
            medications=[med]
        )
        assert bundle.active_medication_count == 1

    def test_empty_bundle_no_raise(self):
        bundle = ClinicalContextBundle(patient_id="empty-patient")
        assert bundle.active_condition_count == 0
        assert bundle.active_medication_count == 0
        assert bundle.fhir_version == "R4"

    def test_bundle_model_dump(self, fhir_patient, fhir_condition_active):
        patient = PatientResource.from_fhir(fhir_patient)
        condition = ConditionResource.from_fhir(fhir_condition_active)
        bundle = ClinicalContextBundle(
            patient_id="test-patient-001",
            patient=patient,
            conditions=[condition]
        )
        dumped = bundle.model_dump()
        assert dumped["patient_id"] == "test-patient-001"
        assert len(dumped["conditions"]) == 1


# ---------------------------------------------------------------------------
# Utility schemas
# ---------------------------------------------------------------------------

class TestUtilitySchemas:
    def test_mcp_tool_result_success(self):
        result = MCPToolResult(success=True, data={"key": "value"})
        assert result.success is True
        assert result.error is None

    def test_mcp_tool_result_failure(self):
        result = MCPToolResult(success=False, error="FHIR 401 Unauthorized")
        assert result.success is False
        assert result.error == "FHIR 401 Unauthorized"

    def test_patient_context_request_defaults(self):
        req = PatientContextRequest(patient_id="pt-001")
        assert req.patient_id == "pt-001"
        assert FHIRResourceType.PATIENT in req.include_resources

    def test_fhir_resource_type_enum(self):
        assert FHIRResourceType.PATIENT == "Patient"
        assert FHIRResourceType.CONDITION == "Condition"
