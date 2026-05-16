# Architecture

> This document describes the internal design of EHR-MCP.
> For integration guides see [epic-setup.md](epic-setup.md) and [fhir-data-contract.md](fhir-data-contract.md).

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
                      │ MCP Tool Calls (stdio)
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
│  - SMART auth       │  │  - Bundle assembly         │
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

## Module Reference

### `server.py` — MCP Tool Registry
Registers all 9 MCP tools using the `mcp` SDK. Each tool has a typed `inputSchema` and maps to either a `FHIRClient` call or a `ClinicalContextPackager` assembly. `get_patient_context` is the primary orchestration entry point — it fans out to multiple FHIR resource fetches and returns a unified `ClinicalContextBundle`.

### `fhir_client.py` — FHIR Abstraction Layer
Async FHIR R4 client. Handles SMART-on-FHIR Backend Services token exchange (RS384 JWT assertion), resource-specific query methods, and error normalization. Vendor-specific quirks are absorbed here so the rest of the stack stays clean.

### `auth.py` — SMART Backend Services
Implements the [SMART Backend Services](https://hl7.org/fhir/smart-app-launch/backend-services.html) auth flow:
1. Generate RS384-signed JWT with `client_id`, `jti`, `exp`
2. POST to `token_url` with `client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`
3. Receive Bearer token scoped to FHIR system scopes
4. Cache token with pre-expiry refresh (60-second buffer)

### `context_packager.py` — Bundle Assembly
Orchestrates parallel FHIR resource fetches via `asyncio.gather`, assembles into a `ClinicalContextBundle`, detects EHR vendor from FHIR `/metadata`, and generates an optional plain-language clinical summary.

### `schemas.py` — Data Contracts
Pydantic v2 models. `ClinicalContextBundle` is the primary output — the typed shape every downstream agent receives. Never change field names without a schema version bump.

---

## Data Flow: `get_patient_context`

```
Agent: get_patient_context(patient_id="12345")
    │
    ▼
server.py → PatientContextRequest (Pydantic validated)
    │
    ▼
context_packager.py → asyncio.gather:
    ├── get_patient()           → Patient resource
    ├── get_conditions()        → Condition list
    ├── get_medications()       → MedicationRequest list
    ├── get_allergies()         → AllergyIntolerance list
    ├── get_observations()      → Observation list
    ├── get_encounters()        → Encounter list
    └── get_diagnostic_reports() → DiagnosticReport list
    │
    ▼
ClinicalContextBundle assembled + vendor detected
    │
    ▼ (if include_summary=True)
Plain-language summary generated
    │
    ▼
TextContent → Agent
```

---

## Design Decisions

**Why MCP over REST?**
MCP tools are natively consumable by agent frameworks without custom client code. A REST API requires each agent team to write a client layer.

**Why vendor normalization inside EHR-MCP?**
Epic, Cerner, and Meditech return FHIR R4 with vendor-specific quirks. Normalizing at the protocol layer means agents never see vendor differences.

**Why `get_patient_context` as the primary tool?**
Clinical workflow agents need multiple resource types simultaneously. One bundle call is more efficient than 7 sequential tool calls and reduces LLM decision surface.

**Why SMART Backend Services (not SMART Launch)?**
Backend agents don't have a user session. Backend Services is the correct OAuth 2.0 flow for system-to-system access — it's what Epic's Non-Patient-Facing App registration requires.

---

## PHI Boundaries

```
┌─────────────────────────────────────────────┐
│  Live EHR / FHIR Server  (PHI in flight)    │
│  Bearer token + TLS only                    │
└──────────────┬──────────────────────────────┘
               │ TLS encrypted
┌──────────────▼──────────────────────────────┐
│  EHR-MCP Server  (PHI in memory only)       │
│  No PHI logged at INFO+                     │
│  No PHI persisted to disk                   │
│  Bearer tokens in-memory, never serialized  │
└──────────────┬──────────────────────────────┘
               │ MCP stdio (local process)
┌──────────────▼──────────────────────────────┐
│  Agent Layer                                │
│  Route raw search_fhir output through       │
│  healthcare-compliance-guardrail in prod    │
└─────────────────────────────────────────────┘
```

See [CLAUDE.md](../CLAUDE.md) for full PHI handling rules.
