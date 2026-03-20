# EHR-MCP Architecture

## Design Philosophy

EHR-MCP is built on one principle: **the interoperability problem should be solved once, not inside every agent.**

Clinical agents — triage, prior auth, care coordination, risk scoring — all need patient context. Without a shared protocol layer, each agent team solves FHIR auth, resource parsing, and data normalization independently. EHR-MCP centralizes that problem and exposes a clean, typed interface any agent can call.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Agent Layer                        │
│  LangGraph │ CrewAI │ LangChain │ AutoGen            │
└─────────────────────┬───────────────────────────────┘
                      │ MCP Tool Calls (stdio / SSE)
┌─────────────────────▼───────────────────────────────┐
│               EHR-MCP Server (server.py)            │
│                                                     │
│  Tool Registry (9 tools)                            │
│  ├── get_patient_context  ← primary orchestration   │
│  ├── get_patient / get_conditions / get_medications │
│  ├── get_observations / get_allergies               │
│  ├── get_encounters / get_diagnostic_reports        │
│  └── search_fhir          ← escape hatch            │
└──────────────┬──────────────────┬───────────────────┘
               │                  │
┌──────────────▼──────┐  ┌────────▼──────────────────┐
│  FHIRClient         │  │  ClinicalContextPackager   │
│  (fhir_client.py)   │  │  (context_packager.py)     │
│                     │  │                            │
│  - SMART auth       │  │  - Assembles bundle        │
│  - Resource fetch   │  │  - Vendor normalization    │
│  - Error handling   │  │  - Plain-language summary  │
└──────────────┬──────┘  └────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│         FHIR R4 Server (Epic / Cerner / Any)        │
│         SMART-on-FHIR Backend Services Auth         │
└─────────────────────────────────────────────────────┘
```

---

## Key Components

### `server.py` — MCP Tool Registry
Registers all 9 MCP tools using the `mcp` SDK. Each tool has a typed `inputSchema` and maps to either a `FHIRClient` call or a `ClinicalContextPackager` assembly. The `get_patient_context` tool is the high-level orchestration entry point — it calls the packager which fans out to multiple FHIR resource fetches and returns a unified `ClinicalContextBundle`.

### `fhir_client.py` — FHIR Abstraction Layer
Async FHIR R4 client responsible for all EHR communication. Handles SMART-on-FHIR Backend Services token exchange (RS384 JWT assertion), resource-specific query methods, and error normalization. Vendor-specific quirks are absorbed here so the rest of the stack stays clean.

### `auth.py` — SMART Backend Services
Implements the [SMART Backend Services](https://hl7.org/fhir/smart-app-launch/backend-services.html) auth flow:
1. Generate RS384-signed JWT with `client_id`, `jti`, `exp`
2. POST to `token_url` with `client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`
3. Receive Bearer token scoped to requested FHIR resources
4. Attach token to all subsequent FHIR requests

### `context_packager.py` — Bundle Assembly
Orchestrates parallel FHIR resource fetches, assembles them into a `ClinicalContextBundle`, detects EHR vendor from FHIR metadata, and generates an optional plain-language clinical summary for LLM consumption.

### `schemas.py` — Data Contracts
Pydantic v2 models defining the message contracts between agents and EHR-MCP. The `ClinicalContextBundle` is the primary output schema — the typed data shape every downstream agent receives. `FHIRResourceType` is an enum enforcing valid resource names at the protocol boundary.

---

## Data Flow: `get_patient_context`

```
Agent calls: get_patient_context(patient_id="12345")
    │
    ▼
server.py: PatientContextRequest validated by Pydantic
    │
    ▼
context_packager.py: fans out to FHIRClient
    ├── get_patient("12345")        → Patient resource
    ├── get_conditions("12345")     → Condition list
    ├── get_medications("12345")    → MedicationRequest list
    ├── get_allergies("12345")      → AllergyIntolerance list
    ├── get_observations("12345")   → Observation list
    ├── get_encounters("12345")     → Encounter list
    └── get_diagnostic_reports()   → DiagnosticReport list
    │
    ▼
ClinicalContextBundle assembled + vendor detected
    │
    ▼ (if include_summary=True)
Plain-language summary generated
    │
    ▼
TextContent returned to agent via MCP protocol
```

---

## FHIR Resource Coverage

| Resource | Tool | Clinical Use Case |
|---|---|---|
| `Patient` | `get_patient` | Demographics, identifiers, contact |
| `Condition` | `get_conditions` | Active diagnoses, ICD-10 codes |
| `MedicationRequest` | `get_medications` | Active Rx, dosage, prescriber |
| `Observation` | `get_observations` | Labs (LOINC), vitals |
| `AllergyIntolerance` | `get_allergies` | Allergy list, reaction severity |
| `Encounter` | `get_encounters` | Visit history, encounter class |
| `DiagnosticReport` | `get_diagnostic_reports` | Imaging, pathology, procedures |
| `Coverage` | `search_fhir` | Insurance coverage (payer, plan) |
| `Claim` | `search_fhir` | Claims data for prior auth workflows |
| `Procedure` | `search_fhir` | Procedure history |

---

## Design Decisions

**Why MCP over a REST API?**
MCP tools are natively consumable by agent frameworks without custom integration code. A REST API would require each agent team to write a client layer. MCP collapses that to a single `MultiServerMCPClient` connection.

**Why vendor normalization inside EHR-MCP?**
Epic, Cerner, and Meditech all return FHIR R4 with vendor-specific extensions and quirks. Normalizing at the protocol layer means agents never see vendor differences — they always receive the same `ClinicalContextBundle` schema.

**Why `get_patient_context` as the primary tool?**
Clinical workflow agents typically need multiple resource types simultaneously. A single bundle call is more efficient than 7 sequential tool calls and reduces LLM decision surface — the agent doesn't need to reason about which resources to fetch.

**Why SMART Backend Services (not SMART Launch)?**
Backend agents don't have a user session. SMART Backend Services is the correct OAuth 2.0 flow for system-to-system access — it's what Epic's Non-Patient-Facing App registration is designed for.
