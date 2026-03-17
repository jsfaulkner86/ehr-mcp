"""
Pydantic schemas for EHR-MCP message contracts.
Defines the standard data shapes that flow between agents and EHR systems.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


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


class PatientContextRequest(BaseModel):
    patient_id: str = Field(..., description="FHIR Patient resource ID")
    include_resources: List[FHIRResourceType] = Field(
        default=[
            FHIRResourceType.PATIENT,
            FHIRResourceType.CONDITION,
            FHIRResourceType.MEDICATION_REQUEST,
            FHIRResourceType.ALLERGY_INTOLERANCE,
        ],
        description="Which FHIR resources to bundle into context"
    )
    encounter_id: Optional[str] = Field(None, description="Scope context to a specific encounter")


class ClinicalContextBundle(BaseModel):
    patient_id: str
    patient: Optional[dict] = None
    conditions: List[dict] = Field(default_factory=list)
    medications: List[dict] = Field(default_factory=list)
    allergies: List[dict] = Field(default_factory=list)
    observations: List[dict] = Field(default_factory=list)
    encounters: List[dict] = Field(default_factory=list)
    diagnostic_reports: List[dict] = Field(default_factory=list)
    vendor: Optional[str] = Field(None, description="EHR vendor detected from FHIR metadata")
    fhir_version: str = Field(default="R4")


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
