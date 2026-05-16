# CLAUDE.md — EHR-MCP

This file gives Claude, Cursor, Windsurf, and other AI coding assistants full context about this codebase. Read this before making any changes.

---

## What This Project Is

**EHR-MCP** is a Model Context Protocol (MCP) server that provides a vendor-agnostic FHIR R4 integration layer for healthcare AI agents. It eliminates the 2–4 week EHR integration tax every clinical AI team pays by providing a reusable, typed, auth-handling protocol layer.

Built and maintained by [The Faulkner Group](https://thefaulknergroupadvisors.com) — Epic-to-Agentic Healthcare AI Architects.

**Core value proposition:**
- An agent calls `get_patient_context(patient_id)`
- EHR-MCP handles SMART-on-FHIR auth (RS384 JWT), FHIR R4 resource fetching, vendor normalization
- The agent receives a typed `ClinicalContextBundle` — not raw FHIR JSON

---

## Architecture

```
Agent (LangGraph / CrewAI / LangChain / AutoGen)
        │
        │  MCP Tool Call
        ▼
   ehr_mcp/server.py          ← MCP server entry point, tool router
        │
        ├── ehr_mcp/auth.py              ← SMART-on-FHIR RS384 JWT auth
        ├── ehr_mcp/fhir_client.py       ← FHIR R4 resource fetcher
        ├── ehr_mcp/context_packager.py  ← ClinicalContextBundle assembly
        └── ehr_mcp/schemas.py           ← Pydantic v2 data contracts
```

**Entry points:**
- `main.py` — runs the MCP server via stdio
- `python -m ehr_mcp.server` — module-level entry (used by Claude Desktop / Cursor configs)

---

## Module Reference

### `ehr_mcp/server.py`
Defines all 9 MCP tools exposed to agent frameworks. Uses `mcp.server.Server` with `@server.list_tools()` and `@server.call_tool()` decorators. Tool routing is a straight `if/elif` block — keep it that way unless tools exceed ~15. Error handling wraps every tool call with a structured `MCPToolResult(success=False, error=...)` fallback.

**Tools registered:**
| Tool | Purpose |
|---|---|
| `get_patient_context` | Primary tool — full `ClinicalContextBundle` |
| `get_patient` | Single Patient FHIR resource |
| `get_conditions` | Active diagnoses (ICD-10) |
| `get_medications` | Active MedicationRequests |
| `get_observations` | Labs + vitals (LOINC) |
| `get_allergies` | AllergyIntolerance resources |
| `get_encounters` | Encounter history |
| `get_diagnostic_reports` | Imaging, pathology reports |
| `search_fhir` | Raw FHIR search (advanced) |

### `ehr_mcp/auth.py`
Implements [SMART on FHIR Backend Services](https://hl7.org/fhir/smart-app-launch/backend-services.html). Generates RS384-signed JWT assertions and exchanges them for Bearer tokens. Handles token caching and pre-expiry refresh (5-min rotation buffer). No user login — system-to-system only.

**Key class:** `SMARTAuthClient`
- `get_access_token()` → cached Bearer token string
- Token refresh is automatic; callers do not manage token lifecycle

### `ehr_mcp/fhir_client.py`
Async FHIR R4 resource fetcher. Uses `httpx.AsyncClient`. All methods are `async`. Injects Bearer token from `SMARTAuthClient` on every request.

**Key class:** `FHIRClient`
- `get_patient(patient_id)` → raw FHIR Patient dict
- `get_conditions(patient_id, count)` → list of Condition dicts
- `get_medications / get_observations / get_allergies / get_encounters / get_diagnostic_reports` — same pattern
- `search_resources(params: ResourceSearchParams)` → raw FHIR Bundle

### `ehr_mcp/context_packager.py`
Assembles individual FHIR resources into a typed `ClinicalContextBundle`. Runs resource fetches concurrently via `asyncio.gather`. Also provides `summarize(bundle)` which generates a plain-language clinical summary string (calls OpenAI if `OPENAI_API_KEY` is set; falls back to structured text summary).

**Key class:** `ClinicalContextPackager`
- `build_context(request: PatientContextRequest)` → `ClinicalContextBundle`
- `summarize(bundle: ClinicalContextBundle)` → `str`

### `ehr_mcp/schemas.py`
All Pydantic v2 models. This is the data contract layer — do not change field names without versioning.

**Key models:**
- `ClinicalContextBundle` — the primary output contract
- `PatientContextRequest` — input validation for `get_patient_context`
- `ResourceSearchParams` — input for `search_fhir`
- `FHIRResourceType` — enum of valid FHIR resource type strings
- `MCPToolResult` — standardized error/success wrapper

---

## Environment Variables

```env
# Required
FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
SMART_TOKEN_URL=https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token
SMART_CLIENT_ID=your_client_id
SMART_PRIVATE_KEY_PATH=./keys/private_key.pem

# Optional
MCP_SERVER_NAME=ehr-mcp
MCP_SERVER_VERSION=0.1.0
OPENAI_API_KEY=your_key_here   # Only for AI-generated clinical summaries
```

Copy `.env.example` to `.env`. Never commit `.env` or private key files.

---

## Development Setup

```bash
git clone https://github.com/jsfaulkner86/ehr-mcp
cd ehr-mcp
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your SMART-on-FHIR credentials to .env
make run
```

For development with test dependencies:
```bash
pip install -r requirements-dev.txt
make test
```

---

## Key Patterns & Conventions

- **Async-first:** All I/O operations are `async`. Do not introduce synchronous HTTP calls.
- **Pydantic v2:** All data contracts use `BaseModel`. Use `model_dump()` not `.dict()`.
- **Config via env:** No hardcoded URLs, credentials, or client IDs anywhere in source.
- **Error handling:** Every MCP tool call is wrapped in try/except. Failures return `MCPToolResult(success=False, error=str(e))` — never raise unhandled exceptions to the agent.
- **Token management:** Never call FHIR endpoints directly without going through `FHIRClient`. Auth is managed internally — don't bypass it.
- **Vendor normalization:** FHIR quirks are handled inside `fhir_client.py`. Don't add vendor-specific logic in `server.py`.

---

## PHI & Security Constraints

⚠️ **This server handles Protected Health Information (PHI).** Before making changes:

- Do **not** log `patient_id`, resource content, or any clinical data at INFO level or above
- Do **not** add any caching layer that persists PHI to disk
- The `search_fhir` tool returns raw FHIR — route through `healthcare-compliance-guardrail` in production pipelines
- Private key files (`*.pem`) must never be committed — `.gitignore` enforces this
- All Bearer tokens are in-memory only and expire; do not persist them
- HIPAA-aligned handling is assumed — add a BAA before connecting to any live EHR endpoint

---

## EHR Compatibility

| Platform | Status |
|---|---|
| Epic (Sandbox) | ✅ Tested |
| Cerner (Oracle Health) | 🔲 Planned |
| Meditech Expanse | 🔲 Planned |
| Any FHIR R4 server | ✅ Via `FHIR_BASE_URL` |

Epic sandbox: [fhir.epic.com](https://fhir.epic.com) — free dev registration.

---

## Related Repos (Healthcare Agent Portfolio)

EHR-MCP is the shared data layer. These agents consume it:

- [`clinical-triage-agent`](https://github.com/jsfaulkner86/clinical-triage-agent)
- [`pph-risk-scoring-agent`](https://github.com/jsfaulkner86/pph-risk-scoring-agent)
- [`prior-auth-research-agent`](https://github.com/jsfaulkner86/prior-auth-research-agent)
- [`healthcare-compliance-guardrail`](https://github.com/jsfaulkner86/healthcare-compliance-guardrail)

---

## What NOT to Do

- Do not refactor the tool router in `server.py` to a registry/dispatch pattern unless tool count exceeds 15 — the current `if/elif` is intentionally readable
- Do not add user-facing OAuth flows — this is backend services auth only
- Do not change `ClinicalContextBundle` field names without a schema version bump
- Do not add synchronous `requests` calls — everything is `httpx` async
- Do not add framework-specific imports to `server.py` — it must stay framework-agnostic

---

*EHR-MCP — The Faulkner Group · [thefaulknergroupadvisors.com](https://thefaulknergroupadvisors.com)*
