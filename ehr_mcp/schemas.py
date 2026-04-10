"""
Pydantic v2 schemas for EHR-MCP typed data contracts.

Every FHIR R4 resource type returned by EHR-MCP has a typed model here.
The goal: agents receive structured, validated data — not raw FHIR JSON.

Design principles:
  - Include clinically and operationally relevant fields only.
    Not every FHIR field. The ones agents actually need.
  - Normalize the Epic/Cerner quirk of code.text vs code.coding[0].display
    using a consistent display_text resolution pattern.
  - All fields Optional with sensible defaults — FHIR resources are
    notoriously incomplete in the wild. Never raise on missing fields.
  - raw_fhir: dict passthrough on every model for advanced consumers
    who need the original FHIR resource alongside the typed interface.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FHIRResourceType(str, Enum):
    PATIENT = "Patient"
    OBSERVATION = "Observation"
    CONDITION = "Condition"
    MEDICATION_REQUEST = "MedicationRequest"
    ENCOUNTER = "Encounter"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    PROCEDURE = "Procedure"
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    COVERAGE = "Coverage"
    CLAIM = "Claim"


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class CodingEntry(BaseModel):
    """A single entry in a FHIR CodeableConcept.coding array."""
    system: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None


class CodeableConcept(BaseModel):
    """FHIR CodeableConcept with resolved display_text."""
    text: Optional[str] = None
    coding: List[CodingEntry] = Field(default_factory=list)
    display_text: Optional[str] = Field(
        None,
        description="Resolved display: code.text → coding[0].display → coding[0].code",
    )

    @model_validator(mode="after")
    def resolve_display_text(self) -> "CodeableConcept":
        if self.display_text:
            return self
        if self.text:
            self.display_text = self.text
        elif self.coding:
            self.display_text = (
                self.coding[0].display
                or self.coding[0].code
            )
        return self


class Quantity(BaseModel):
    """FHIR Quantity — numeric value with unit."""
    value: Optional[float] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None


class ReferenceRange(BaseModel):
    """FHIR Observation.referenceRange entry."""
    low: Optional[Quantity] = None
    high: Optional[Quantity] = None
    text: Optional[str] = None


class HumanName(BaseModel):
    """FHIR HumanName — patient or practitioner name."""
    use: Optional[str] = None
    text: Optional[str] = None
    family: Optional[str] = None
    given: List[str] = Field(default_factory=list)
    prefix: List[str] = Field(default_factory=list)
    suffix: List[str] = Field(default_factory=list)
    display_name: Optional[str] = None

    @model_validator(mode="after")
    def resolve_display_name(self) -> "HumanName":
        if self.display_name:
            return self
        if self.text:
            self.display_name = self.text
        else:
            parts = self.prefix + self.given + ([self.family] if self.family else []) + self.suffix
            self.display_name = " ".join(parts).strip() or None
        return self


class ContactPoint(BaseModel):
    """FHIR ContactPoint — phone, email, etc."""
    system: Optional[str] = None   # phone | fax | email | url
    value: Optional[str] = None
    use: Optional[str] = None      # home | work | mobile


class Address(BaseModel):
    """FHIR Address."""
    use: Optional[str] = None
    line: List[str] = Field(default_factory=list)
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = Field(None, alias="postalCode")
    country: Optional[str] = None

    model_config = {"populate_by_name": True}


class DosageInstruction(BaseModel):
    """Simplified FHIR DosageInstruction."""
    text: Optional[str] = None
    route: Optional[CodeableConcept] = None
    dose_quantity: Optional[Quantity] = None
    frequency_text: Optional[str] = None


class ReactionEntry(BaseModel):
    """A single AllergyIntolerance reaction."""
    substance: Optional[CodeableConcept] = None
    manifestations: List[CodeableConcept] = Field(default_factory=list)
    severity: Optional[str] = None   # mild | moderate | severe
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# FHIR Resource Models
# ---------------------------------------------------------------------------

class PatientResource(BaseModel):
    """
    Typed representation of a FHIR R4 Patient resource.

    Covers the fields agents need for clinical context:
    identity, demographics, contact, and administrative.
    """
    resource_type: Literal["Patient"] = Field(default="Patient", alias="resourceType")
    id: Optional[str] = None
    active: Optional[bool] = None

    # Identity
    name: List[HumanName] = Field(default_factory=list)
    display_name: Optional[str] = None   # resolved from name[0]
    birth_date: Optional[str] = Field(None, alias="birthDate")   # FHIR date string: YYYY-MM-DD
    gender: Optional[str] = None         # male | female | other | unknown
    deceased_boolean: Optional[bool] = Field(None, alias="deceasedBoolean")
    deceased_date_time: Optional[str] = Field(None, alias="deceasedDateTime")

    # Contact
    telecom: List[ContactPoint] = Field(default_factory=list)
    address: List[Address] = Field(default_factory=list)

    # Administrative
    marital_status: Optional[CodeableConcept] = Field(None, alias="maritalStatus")
    language: Optional[str] = None
    race: Optional[str] = None           # resolved from US Core extension
    ethnicity: Optional[str] = None      # resolved from US Core extension

    # Passthrough
    raw_fhir: Optional[dict[str, Any]] = Field(
        None,
        description="Original FHIR Patient resource for advanced consumers.",
        exclude=True,   # excluded from .model_dump() by default
    )

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def resolve_display_name(self) -> "PatientResource":
        if not self.display_name and self.name:
            self.display_name = self.name[0].display_name
        return self

    @classmethod
    def from_fhir(cls, raw: dict[str, Any]) -> "PatientResource":
        """Construct from a raw FHIR Patient resource dict."""
        instance = cls.model_validate(raw)
        object.__setattr__(instance, "raw_fhir", raw)
        # Resolve US Core race/ethnicity extensions
        for ext in raw.get("extension", []):
            url = ext.get("url", "")
            if "us-core-race" in url:
                for sub in ext.get("extension", []):
                    if sub.get("url") == "text":
                        object.__setattr__(instance, "race", sub.get("valueString"))
            elif "us-core-ethnicity" in url:
                for sub in ext.get("extension", []):
                    if sub.get("url") == "text":
                        object.__setattr__(instance, "ethnicity", sub.get("valueString"))
        return instance


class ConditionResource(BaseModel):
    """
    Typed representation of a FHIR R4 Condition resource.

    Focuses on active diagnoses with ICD-10 codes.
    Used by triage agents, risk scoring agents, prior auth agents.
    """
    resource_type: Literal["Condition"] = Field(default="Condition", alias="resourceType")
    id: Optional[str] = None

    # Core clinical fields
    code: Optional[CodeableConcept] = None
    display_text: Optional[str] = None   # resolved shortcut: condition name for agents
    icd10_code: Optional[str] = None     # resolved from code.coding where system = ICD-10
    snomed_code: Optional[str] = None    # resolved from code.coding where system = SNOMED

    # Status
    clinical_status: Optional[CodeableConcept] = Field(None, alias="clinicalStatus")
    verification_status: Optional[CodeableConcept] = Field(None, alias="verificationStatus")
    is_active: Optional[bool] = None     # resolved: clinicalStatus.code == "active"

    # Categorization
    category: List[CodeableConcept] = Field(default_factory=list)
    severity: Optional[CodeableConcept] = None

    # Timing
    onset_date_time: Optional[str] = Field(None, alias="onsetDateTime")
    onset_period_start: Optional[str] = None
    abatement_date_time: Optional[str] = Field(None, alias="abatementDateTime")
    recorded_date: Optional[str] = Field(None, alias="recordedDate")

    # Context
    encounter_id: Optional[str] = None   # resolved from encounter.reference
    subject_id: Optional[str] = None     # resolved from subject.reference

    raw_fhir: Optional[dict[str, Any]] = Field(None, exclude=True)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def resolve_derived_fields(self) -> "ConditionResource":
        if self.code and not self.display_text:
            self.display_text = self.code.display_text
        if self.clinical_status and not self.is_active:
            status_text = (
                self.clinical_status.text
                or (self.clinical_status.coding[0].code if self.clinical_status.coding else None)
            )
            self.is_active = status_text == "active" if status_text else None
        return self

    @classmethod
    def from_fhir(cls, raw: dict[str, Any]) -> "ConditionResource":
        instance = cls.model_validate(raw)
        object.__setattr__(instance, "raw_fhir", raw)
        # Resolve ICD-10 and SNOMED codes from coding array
        for coding in raw.get("code", {}).get("coding", []):
            system = coding.get("system", "").lower()
            if "icd-10" in system or "icd10" in system:
                object.__setattr__(instance, "icd10_code", coding.get("code"))
            elif "snomed" in system:
                object.__setattr__(instance, "snomed_code", coding.get("code"))
        # Resolve encounter and subject references
        enc_ref = raw.get("encounter", {}).get("reference", "")
        if enc_ref:
            object.__setattr__(instance, "encounter_id", enc_ref.split("/")[-1])
        subj_ref = raw.get("subject", {}).get("reference", "")
        if subj_ref:
            object.__setattr__(instance, "subject_id", subj_ref.split("/")[-1])
        return instance


class MedicationResource(BaseModel):
    """
    Typed representation of a FHIR R4 MedicationRequest resource.

    Covers active prescriptions with dosage and prescriber context.
    Used by prior auth agents, clinical triage agents.
    """
    resource_type: Literal["MedicationRequest"] = Field(
        default="MedicationRequest", alias="resourceType"
    )
    id: Optional[str] = None

    # Medication identity
    medication_code: Optional[CodeableConcept] = Field(
        None, alias="medicationCodeableConcept"
    )
    display_text: Optional[str] = None   # resolved shortcut: drug name for agents
    rxnorm_code: Optional[str] = None    # resolved from coding where system = RxNorm

    # Status
    status: Optional[str] = None   # active | on-hold | cancelled | completed | stopped
    intent: Optional[str] = None   # proposal | plan | order | original-order

    # Dosage
    dosage_instruction: List[DosageInstruction] = Field(
        default_factory=list, alias="dosageInstruction"
    )
    dosage_text: Optional[str] = None   # resolved from dosageInstruction[0].text

    # Prescriber
    requester_id: Optional[str] = None   # resolved from requester.reference
    requester_display: Optional[str] = None

    # Context
    authored_on: Optional[str] = Field(None, alias="authoredOn")
    subject_id: Optional[str] = None
    encounter_id: Optional[str] = None

    # Supply
    days_supply: Optional[int] = None
    quantity: Optional[Quantity] = None

    raw_fhir: Optional[dict[str, Any]] = Field(None, exclude=True)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def resolve_derived_fields(self) -> "MedicationResource":
        if self.medication_code and not self.display_text:
            self.display_text = self.medication_code.display_text
        if self.dosage_instruction and not self.dosage_text:
            self.dosage_text = self.dosage_instruction[0].text
        return self

    @classmethod
    def from_fhir(cls, raw: dict[str, Any]) -> "MedicationResource":
        instance = cls.model_validate(raw)
        object.__setattr__(instance, "raw_fhir", raw)
        # RxNorm code
        for coding in raw.get("medicationCodeableConcept", {}).get("coding", []):
            if "rxnorm" in coding.get("system", "").lower():
                object.__setattr__(instance, "rxnorm_code", coding.get("code"))
        # Requester
        requester = raw.get("requester", {})
        if requester.get("reference"):
            object.__setattr__(instance, "requester_id", requester["reference"].split("/")[-1])
        if requester.get("display"):
            object.__setattr__(instance, "requester_display", requester["display"])
        # Subject / encounter refs
        subj = raw.get("subject", {}).get("reference", "")
        if subj:
            object.__setattr__(instance, "subject_id", subj.split("/")[-1])
        enc = raw.get("encounter", {}).get("reference", "")
        if enc:
            object.__setattr__(instance, "encounter_id", enc.split("/")[-1])
        return instance


class AllergyResource(BaseModel):
    """
    Typed representation of a FHIR R4 AllergyIntolerance resource.

    Covers substance, reaction severity, and category.
    Critical for prior auth and medication safety agents.
    """
    resource_type: Literal["AllergyIntolerance"] = Field(
        default="AllergyIntolerance", alias="resourceType"
    )
    id: Optional[str] = None

    # Substance
    code: Optional[CodeableConcept] = None
    display_text: Optional[str] = None   # resolved shortcut: allergen name

    # Classification
    clinical_status: Optional[CodeableConcept] = Field(None, alias="clinicalStatus")
    verification_status: Optional[CodeableConcept] = Field(None, alias="verificationStatus")
    allergy_type: Optional[str] = Field(
        None, alias="type"
    )   # allergy | intolerance
    category: List[str] = Field(
        default_factory=list
    )   # food | medication | environment | biologic
    criticality: Optional[str] = None   # low | high | unable-to-assess

    # Reactions
    reaction: List[ReactionEntry] = Field(default_factory=list)
    highest_severity: Optional[str] = None   # resolved from reactions

    # Timing
    onset_date_time: Optional[str] = Field(None, alias="onsetDateTime")
    recorded_date: Optional[str] = Field(None, alias="recordedDate")

    subject_id: Optional[str] = None
    raw_fhir: Optional[dict[str, Any]] = Field(None, exclude=True)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def resolve_derived_fields(self) -> "AllergyResource":
        if self.code and not self.display_text:
            self.display_text = self.code.display_text
        if self.reaction and not self.highest_severity:
            severity_rank = {"severe": 3, "moderate": 2, "mild": 1}
            best = max(
                (r.severity for r in self.reaction if r.severity),
                key=lambda s: severity_rank.get(s, 0),
                default=None,
            )
            self.highest_severity = best
        return self

    @classmethod
    def from_fhir(cls, raw: dict[str, Any]) -> "AllergyResource":
        instance = cls.model_validate(raw)
        object.__setattr__(instance, "raw_fhir", raw)
        subj = raw.get("patient", {}).get("reference", "")
        if subj:
            object.__setattr__(instance, "subject_id", subj.split("/")[-1])
        return instance


class ObservationResource(BaseModel):
    """
    Typed representation of a FHIR R4 Observation resource.

    Covers labs and vitals with LOINC codes, values, units,
    and reference ranges. Used by risk scoring and triage agents.
    """
    resource_type: Literal["Observation"] = Field(default="Observation", alias="resourceType")
    id: Optional[str] = None

    # Identity
    code: Optional[CodeableConcept] = None
    display_text: Optional[str] = None   # resolved shortcut: test/vital name
    loinc_code: Optional[str] = None     # resolved from code.coding where system = LOINC

    # Status
    status: Optional[str] = None   # final | preliminary | amended | corrected | cancelled

    # Category
    category: List[CodeableConcept] = Field(default_factory=list)
    observation_category: Optional[str] = None   # laboratory | vital-signs | social-history

    # Value
    value_quantity: Optional[Quantity] = Field(None, alias="valueQuantity")
    value_string: Optional[str] = Field(None, alias="valueString")
    value_codeable_concept: Optional[CodeableConcept] = Field(
        None, alias="valueCodeableConcept"
    )
    value_display: Optional[str] = None   # resolved: human-readable value + unit

    # Reference range
    reference_range: List[ReferenceRange] = Field(
        default_factory=list, alias="referenceRange"
    )
    interpretation: Optional[CodeableConcept] = None   # N | H | L | A etc.

    # Timing
    effective_date_time: Optional[str] = Field(None, alias="effectiveDateTime")
    issued: Optional[str] = None

    # Context
    subject_id: Optional[str] = None
    encounter_id: Optional[str] = None
    performer_display: Optional[str] = None

    raw_fhir: Optional[dict[str, Any]] = Field(None, exclude=True)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def resolve_derived_fields(self) -> "ObservationResource":
        if self.code and not self.display_text:
            self.display_text = self.code.display_text
        if self.value_quantity and not self.value_display:
            val = self.value_quantity.value
            unit = self.value_quantity.unit or ""
            self.value_display = f"{val} {unit}".strip() if val is not None else None
        elif self.value_string and not self.value_display:
            self.value_display = self.value_string
        elif self.value_codeable_concept and not self.value_display:
            self.value_display = self.value_codeable_concept.display_text
        if self.category and not self.observation_category:
            self.observation_category = (
                self.category[0].coding[0].code
                if self.category[0].coding
                else self.category[0].text
            )
        return self

    @classmethod
    def from_fhir(cls, raw: dict[str, Any]) -> "ObservationResource":
        instance = cls.model_validate(raw)
        object.__setattr__(instance, "raw_fhir", raw)
        for coding in raw.get("code", {}).get("coding", []):
            if "loinc" in coding.get("system", "").lower():
                object.__setattr__(instance, "loinc_code", coding.get("code"))
        subj = raw.get("subject", {}).get("reference", "")
        if subj:
            object.__setattr__(instance, "subject_id", subj.split("/")[-1])
        enc = raw.get("encounter", {}).get("reference", "")
        if enc:
            object.__setattr__(instance, "encounter_id", enc.split("/")[-1])
        performers = raw.get("performer", [])
        if performers:
            object.__setattr__(instance, "performer_display", performers[0].get("display"))
        return instance


class EncounterResource(BaseModel):
    """
    Typed representation of a FHIR R4 Encounter resource.

    Covers visit type, class, status, dates, and location.
    Used by triage agents and context-building workflows.
    """
    resource_type: Literal["Encounter"] = Field(default="Encounter", alias="resourceType")
    id: Optional[str] = None

    # Status
    status: Optional[str] = None   # planned | in-progress | finished | cancelled

    # Classification
    encounter_class: Optional[CodingEntry] = Field(
        None, alias="class"
    )   # AMB | IMP | EMER | HH etc.
    encounter_class_display: Optional[str] = None
    encounter_type: List[CodeableConcept] = Field(default_factory=list, alias="type")
    display_text: Optional[str] = None   # resolved: encounter type name

    # Service
    service_type: Optional[CodeableConcept] = Field(None, alias="serviceType")
    priority: Optional[CodeableConcept] = None
    reason_code: List[CodeableConcept] = Field(default_factory=list, alias="reasonCode")

    # Timing
    period_start: Optional[str] = None   # resolved from period.start
    period_end: Optional[str] = None     # resolved from period.end
    length_minutes: Optional[int] = None

    # Location
    location_display: Optional[str] = None   # resolved from location[0].location.display
    service_provider_display: Optional[str] = None

    # Participants
    practitioner_display: Optional[str] = None   # resolved from participant[0]

    subject_id: Optional[str] = None
    raw_fhir: Optional[dict[str, Any]] = Field(None, exclude=True)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def resolve_derived_fields(self) -> "EncounterResource":
        if self.encounter_class and not self.encounter_class_display:
            self.encounter_class_display = (
                self.encounter_class.display or self.encounter_class.code
            )
        if self.encounter_type and not self.display_text:
            self.display_text = self.encounter_type[0].display_text
        return self

    @classmethod
    def from_fhir(cls, raw: dict[str, Any]) -> "EncounterResource":
        instance = cls.model_validate(raw)
        object.__setattr__(instance, "raw_fhir", raw)
        # Period
        period = raw.get("period", {})
        if period.get("start"):
            object.__setattr__(instance, "period_start", period["start"])
        if period.get("end"):
            object.__setattr__(instance, "period_end", period["end"])
        # Location
        locations = raw.get("location", [])
        if locations:
            object.__setattr__(
                instance, "location_display",
                locations[0].get("location", {}).get("display")
            )
        # Participants
        participants = raw.get("participant", [])
        if participants:
            object.__setattr__(
                instance, "practitioner_display",
                participants[0].get("individual", {}).get("display")
            )
        # Service provider
        sp = raw.get("serviceProvider", {}).get("display")
        if sp:
            object.__setattr__(instance, "service_provider_display", sp)
        # Subject
        subj = raw.get("subject", {}).get("reference", "")
        if subj:
            object.__setattr__(instance, "subject_id", subj.split("/")[-1])
        return instance


class DiagnosticReportResource(BaseModel):
    """
    Typed representation of a FHIR R4 DiagnosticReport resource.

    Covers imaging, pathology, and procedure reports.
    Used by clinical context assembly and documentation agents.
    """
    resource_type: Literal["DiagnosticReport"] = Field(
        default="DiagnosticReport", alias="resourceType"
    )
    id: Optional[str] = None

    # Identity
    code: Optional[CodeableConcept] = None
    display_text: Optional[str] = None

    # Status
    status: Optional[str] = None   # registered | partial | final | amended | corrected

    # Category
    category: List[CodeableConcept] = Field(default_factory=list)
    report_category: Optional[str] = None   # resolved: LAB | RAD | PATH

    # Timing
    effective_date_time: Optional[str] = Field(None, alias="effectiveDateTime")
    issued: Optional[str] = None

    # Content
    conclusion: Optional[str] = None
    conclusion_code: List[CodeableConcept] = Field(
        default_factory=list, alias="conclusionCode"
    )
    presented_form_titles: List[str] = Field(
        default_factory=list
    )   # resolved from presentedForm[].title

    # Performers
    performer_display: Optional[str] = None
    results_interpreter_display: Optional[str] = None

    # Linked observations
    result_ids: List[str] = Field(
        default_factory=list
    )   # resolved from result[].reference

    subject_id: Optional[str] = None
    encounter_id: Optional[str] = None
    raw_fhir: Optional[dict[str, Any]] = Field(None, exclude=True)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def resolve_derived_fields(self) -> "DiagnosticReportResource":
        if self.code and not self.display_text:
            self.display_text = self.code.display_text
        if self.category and not self.report_category:
            self.report_category = (
                self.category[0].coding[0].code
                if self.category[0].coding
                else self.category[0].text
            )
        return self

    @classmethod
    def from_fhir(cls, raw: dict[str, Any]) -> "DiagnosticReportResource":
        instance = cls.model_validate(raw)
        object.__setattr__(instance, "raw_fhir", raw)
        # Performers
        performers = raw.get("performer", [])
        if performers:
            object.__setattr__(instance, "performer_display", performers[0].get("display"))
        interpreters = raw.get("resultsInterpreter", [])
        if interpreters:
            object.__setattr__(
                instance, "results_interpreter_display", interpreters[0].get("display")
            )
        # Presented form titles
        titles = [pf.get("title") for pf in raw.get("presentedForm", []) if pf.get("title")]
        if titles:
            object.__setattr__(instance, "presented_form_titles", titles)
        # Result references
        result_ids = [r.get("reference", "").split("/")[-1] for r in raw.get("result", [])]
        if result_ids:
            object.__setattr__(instance, "result_ids", [r for r in result_ids if r])
        # Subject / encounter
        subj = raw.get("subject", {}).get("reference", "")
        if subj:
            object.__setattr__(instance, "subject_id", subj.split("/")[-1])
        enc = raw.get("encounter", {}).get("reference", "")
        if enc:
            object.__setattr__(instance, "encounter_id", enc.split("/")[-1])
        return instance


# ---------------------------------------------------------------------------
# ClinicalContextBundle — the primary agent-facing data contract
# ---------------------------------------------------------------------------

class ClinicalContextBundle(BaseModel):
    """
    The core output of EHR-MCP.

    A fully typed, vendor-normalized clinical context bundle.
    Every agent in the portfolio receives this — not raw FHIR JSON.

    All fields are Optional with empty defaults.
    FHIR resources are notoriously incomplete across vendors;
    agents must handle None gracefully on any field.
    """
    patient_id: str
    patient: Optional[PatientResource] = None
    conditions: List[ConditionResource] = Field(default_factory=list)
    medications: List[MedicationResource] = Field(default_factory=list)
    allergies: List[AllergyResource] = Field(default_factory=list)
    observations: List[ObservationResource] = Field(default_factory=list)
    encounters: List[EncounterResource] = Field(default_factory=list)
    diagnostic_reports: List[DiagnosticReportResource] = Field(default_factory=list)

    # Metadata
    vendor: Optional[str] = Field(None, description="EHR vendor detected from FHIR /metadata")
    fhir_version: str = Field(default="R4")
    bundle_generated_at: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp of when this bundle was assembled",
    )

    # Active issue counts — convenience for agent prompts
    active_condition_count: int = Field(default=0)
    active_medication_count: int = Field(default=0)

    @model_validator(mode="after")
    def compute_counts(self) -> "ClinicalContextBundle":
        self.active_condition_count = sum(
            1 for c in self.conditions if c.is_active
        )
        self.active_medication_count = sum(
            1 for m in self.medications if m.status == "active"
        )
        return self


# ---------------------------------------------------------------------------
# Request / utility schemas (unchanged from v0.1.0)
# ---------------------------------------------------------------------------

class PatientContextRequest(BaseModel):
    patient_id: str = Field(..., description="FHIR Patient resource ID")
    include_resources: List[FHIRResourceType] = Field(
        default=[
            FHIRResourceType.PATIENT,
            FHIRResourceType.CONDITION,
            FHIRResourceType.MEDICATION_REQUEST,
            FHIRResourceType.ALLERGY_INTOLERANCE,
        ],
        description="Which FHIR resources to bundle into context",
    )
    encounter_id: Optional[str] = Field(
        None, description="Scope context to a specific encounter"
    )


class ResourceSearchParams(BaseModel):
    resource_type: FHIRResourceType
    patient_id: Optional[str] = None
    encounter_id: Optional[str] = None
    count: int = Field(default=10, le=100)
    additional_params: Optional[dict] = None


class MCPToolResult(BaseModel):
    success: bool
    data: Optional[dict | list] = None
    error: Optional[str] = None
    vendor: Optional[str] = None
    fhir_base_url: Optional[str] = None
