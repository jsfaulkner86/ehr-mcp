# Changelog

All notable changes to EHR-MCP are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [0.1.0] — 2026-05-16

### Added
- **MCP Server** (`ehr_mcp/server.py`) — 9 MCP tools exposed via Model Context Protocol stdio transport
  - `get_patient_context` — Full `ClinicalContextBundle` assembly (primary tool)
  - `get_patient` — Single Patient FHIR resource
  - `get_conditions` — Active diagnoses with ICD-10 codes
  - `get_medications` — Active MedicationRequests with dosage
  - `get_observations` — Labs and vitals with LOINC codes
  - `get_allergies` — AllergyIntolerance resources with severity
  - `get_encounters` — Encounter history with type and dates
  - `get_diagnostic_reports` — Imaging and pathology reports
  - `search_fhir` — Raw FHIR R4 search for advanced agent use cases
- **SMART-on-FHIR Auth** (`ehr_mcp/auth.py`) — RS384 JWT Backend Services flow; token caching with pre-expiry refresh
- **FHIR R4 Client** (`ehr_mcp/fhir_client.py`) — Async `httpx`-based resource fetcher; vendor normalization layer
- **Clinical Context Packager** (`ehr_mcp/context_packager.py`) — Concurrent resource assembly via `asyncio.gather`; optional OpenAI plain-language summary
- **Pydantic v2 Schemas** (`ehr_mcp/schemas.py`) — Typed data contracts: `ClinicalContextBundle`, `PatientContextRequest`, `ResourceSearchParams`, `FHIRResourceType`, `MCPToolResult`
- **Docker support** — `Dockerfile` + `docker-compose.yml` for containerized deployment
- **Claude Desktop integration** — `claude_desktop_config.json` example in README
- **Cursor / Windsurf integration** — `.cursor/mcp.json` config example in README
- **Framework compatibility** — LangGraph, LangChain, CrewAI, AutoGen via `langchain-mcp-adapters`
- **Epic Sandbox tested** — Validated against `fhir.epic.com` R4 endpoint
- **Academic citation** — Aligned with arXiv:2509.15957 (EHR-MCP real-world evaluation)
- **CLAUDE.md** — AI assistant context file for Claude, Cursor, and Windsurf
- **Makefile** — `install`, `install-dev`, `run`, `test`, `lint`, `format`, `clean`, `docker-build`, `docker-run`, `keys`
- **`.mcp.json`** — MCP server configuration for tool-aware AI assistants

### Architecture
- Vendor-agnostic FHIR abstraction via `FHIR_BASE_URL` env var
- PHI never logged at INFO level or above
- Backend Services auth only — no user-facing OAuth flows
- Framework-agnostic server — no LangChain/LangGraph imports in `server.py`

### Known Limitations
- Cerner (Oracle Health) and Meditech Expanse not yet validated (planned)
- Bidirectional FHIR write support not yet implemented
- `Coverage` + `Claim` tools for prior auth workflows pending
- No OpenAPI/REST transport — stdio only in this release

---

## Roadmap

- [ ] `v0.2.0` — Epic sandbox end-to-end integration test suite + CI badge
- [ ] `v0.2.0` — `requirements-dev.txt` + `pyproject.toml` + `pytest` test suite
- [ ] `v0.3.0` — Cerner (Oracle Health) validation
- [ ] `v0.3.0` — Bidirectional write support (`Task`, `Communication`, `ServiceRequest`)
- [ ] `v0.4.0` — `Coverage` + `Claim` tools for prior auth workflows
- [ ] `v0.5.0` — OpenAPI spec + REST transport option

---

*Part of The Faulkner Group's healthcare agentic AI portfolio → [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*
