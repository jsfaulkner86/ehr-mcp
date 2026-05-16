# FHIR Data Contract

Reference for the `ClinicalContextBundle` — the typed data contract every agent receives from EHR-MCP.

---

## ClinicalContextBundle

The primary output of `get_patient_context`. A Pydantic v2 model — fully typed, vendor-normalized.

```python
class ClinicalContextBundle(BaseModel):
    patient_id: str
    patient: Optional[PatientResource]
    conditions: List[ConditionResource]
    medications: List[MedicationResource]
    allergies: List[AllergyResource]
    observations: List[ObservationResource]
    encounters: List[EncounterResource]
    diagnostic_reports: List[DiagnosticReportResource]

    # Metadata
    vendor: Optional[str]            # EHR vendor detected from /metadata
    fhir_version: str                # Always "R4"
    bundle_generated_at: Optional[str]

    # Convenience counts for agent prompts
    active_condition_count: int
    active_medication_count: int
```

> All list fields default to `[]`. All Optional fields default to `None`. FHIR resources are incomplete in the wild — agents must handle `None` gracefully on every field.

---

## Resource Models

### PatientResource

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | `str` | `Patient.id` | FHIR resource ID |
| `display_name` | `str` | resolved | `name[0]` assembled |
| `birth_date` | `str` | `Patient.birthDate` | `YYYY-MM-DD` |
| `gender` | `str` | `Patient.gender` | `male\|female\|other\|unknown` |
| `telecom` | `List[ContactPoint]` | `Patient.telecom` | phone, email |
| `address` | `List[Address]` | `Patient.address` | |
| `race` | `str` | US Core extension | resolved from `us-core-race` |
| `ethnicity` | `str` | US Core extension | resolved from `us-core-ethnicity` |

### ConditionResource

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | `str` | `Condition.id` | |
| `display_text` | `str` | resolved | condition name for agents |
| `icd10_code` | `str` | resolved | from `code.coding` where system=ICD-10 |
| `snomed_code` | `str` | resolved | from `code.coding` where system=SNOMED |
| `is_active` | `bool` | resolved | `clinicalStatus.code == "active"` |
| `onset_date_time` | `str` | `Condition.onsetDateTime` | ISO 8601 |
| `subject_id` | `str` | resolved | from `subject.reference` |

### MedicationResource

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | `str` | `MedicationRequest.id` | |
| `display_text` | `str` | resolved | drug name for agents |
| `rxnorm_code` | `str` | resolved | from `medicationCodeableConcept.coding` |
| `status` | `str` | `MedicationRequest.status` | `active\|on-hold\|completed` |
| `dosage_text` | `str` | resolved | `dosageInstruction[0].text` |
| `authored_on` | `str` | `MedicationRequest.authoredOn` | |
| `requester_display` | `str` | resolved | prescriber name |

### ObservationResource

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | `str` | `Observation.id` | |
| `display_text` | `str` | resolved | test or vital name |
| `loinc_code` | `str` | resolved | from `code.coding` where system=LOINC |
| `status` | `str` | `Observation.status` | `final\|preliminary\|amended` |
| `value_display` | `str` | resolved | `"11.2 g/dL"` format |
| `observation_category` | `str` | resolved | `laboratory\|vital-signs` |
| `effective_date_time` | `str` | `Observation.effectiveDateTime` | |
| `reference_range` | `List[ReferenceRange]` | `Observation.referenceRange` | |

### AllergyResource

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | `str` | `AllergyIntolerance.id` | |
| `display_text` | `str` | resolved | allergen name |
| `criticality` | `str` | `AllergyIntolerance.criticality` | `low\|high\|unable-to-assess` |
| `highest_severity` | `str` | resolved | worst reaction severity |
| `category` | `List[str]` | `AllergyIntolerance.category` | `medication\|food\|environment` |

### EncounterResource

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | `str` | `Encounter.id` | |
| `display_text` | `str` | resolved | encounter type name |
| `encounter_class_display` | `str` | resolved | `AMB\|IMP\|EMER` |
| `status` | `str` | `Encounter.status` | `finished\|in-progress\|planned` |
| `period_start` | `str` | resolved | from `period.start` |
| `period_end` | `str` | resolved | from `period.end` |
| `service_provider_display` | `str` | resolved | facility name |

---

## display_text Resolution

Every resource model resolves a `display_text` field using this waterfall:

```
code.text  →  code.coding[0].display  →  code.coding[0].code  →  None
```

This handles Epic's inconsistent use of `code.text` vs `coding[0].display` without agent-side logic.

---

## Vendor Normalization

Vendor-specific FHIR quirks absorbed by `fhir_client.py`:

| Vendor | Known Quirk | Handling |
|---|---|---|
| Epic | `code.text` sometimes absent; uses `coding[0].display` | `display_text` waterfall resolver |
| Epic | US Core race/ethnicity in extensions | `PatientResource.from_fhir()` resolves extensions |
| General | `subject.reference` as `Patient/id` or just `id` | `.split("/")[-1]` normalization |
| General | Missing `clinicalStatus` on Condition | `is_active` defaults to `None`, not `False` |

---

## Schema Versioning

The current schema version is `0.1.0` (matches `MCP_SERVER_VERSION`).

**Breaking change rules:**
- Removing or renaming a field on `ClinicalContextBundle` or any resource model = breaking change → minor version bump
- Adding Optional fields = non-breaking → patch version bump
- Changing a field type = breaking change → minor version bump

Downstream agents should pin to a compatible version range in their dependency specs.
