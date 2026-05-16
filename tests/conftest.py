"""
pytest fixtures shared across the EHR-MCP test suite.

All FHIR and SMART auth calls are mocked — no live EHR credentials required.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Minimal synthetic FHIR R4 resource fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fhir_patient():
    return {
        "resourceType": "Patient",
        "id": "test-patient-001",
        "active": True,
        "name": [{"use": "official", "family": "Johnson", "given": ["Maria"]}],
        "birthDate": "1985-03-14",
        "gender": "female",
        "telecom": [{"system": "phone", "value": "555-1234", "use": "home"}],
        "address": [{"use": "home", "city": "Detroit", "state": "MI", "postalCode": "48201"}],
    }


@pytest.fixture
def fhir_condition_active():
    return {
        "resourceType": "Condition",
        "id": "cond-001",
        "clinicalStatus": {
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]
        },
        "verificationStatus": {
            "coding": [{"code": "confirmed"}]
        },
        "code": {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                    "code": "O14.10",
                    "display": "Pre-eclampsia, unspecified trimester"
                }
            ],
            "text": "Pre-eclampsia"
        },
        "subject": {"reference": "Patient/test-patient-001"},
        "recordedDate": "2026-01-15",
    }


@pytest.fixture
def fhir_medication_active():
    return {
        "resourceType": "MedicationRequest",
        "id": "med-001",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "1049502",
                    "display": "Labetalol 200 MG"
                }
            ],
            "text": "Labetalol 200 MG Oral Tablet"
        },
        "dosageInstruction": [{"text": "200mg twice daily"}],
        "subject": {"reference": "Patient/test-patient-001"},
        "authoredOn": "2026-01-15",
    }


@pytest.fixture
def fhir_allergy():
    return {
        "resourceType": "AllergyIntolerance",
        "id": "allergy-001",
        "clinicalStatus": {
            "coding": [{"code": "active"}]
        },
        "type": "allergy",
        "category": ["medication"],
        "criticality": "high",
        "code": {
            "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "7980", "display": "Penicillin"}],
            "text": "Penicillin"
        },
        "reaction": [{"severity": "severe", "manifestation": [{"text": "Anaphylaxis"}]}],
        "patient": {"reference": "Patient/test-patient-001"},
    }


@pytest.fixture
def fhir_observation_lab():
    return {
        "resourceType": "Observation",
        "id": "obs-001",
        "status": "final",
        "category": [{
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]
        }],
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "2857-1", "display": "PSA [Mass/volume]"}],
            "text": "Hemoglobin"
        },
        "valueQuantity": {"value": 11.2, "unit": "g/dL"},
        "subject": {"reference": "Patient/test-patient-001"},
        "effectiveDateTime": "2026-02-01T09:00:00Z",
    }


@pytest.fixture
def fhir_encounter():
    return {
        "resourceType": "Encounter",
        "id": "enc-001",
        "status": "finished",
        "class": {"code": "AMB", "display": "Ambulatory"},
        "type": [{"text": "Prenatal visit", "coding": [{"display": "Prenatal visit"}]}],
        "subject": {"reference": "Patient/test-patient-001"},
        "period": {"start": "2026-01-15T10:00:00Z", "end": "2026-01-15T10:45:00Z"},
        "serviceProvider": {"display": "Metro Women's Health"},
    }


@pytest.fixture
def mock_bearer_token():
    return "mock-bearer-token-abc123"
