# Epic FHIR Sandbox Setup

Step-by-step guide to connecting EHR-MCP to Epic's FHIR R4 sandbox.

---

## Prerequisites

- Python 3.11+
- `openssl` available on your PATH (`make keys` uses it)
- An Epic on FHIR developer account (free): [fhir.epic.com](https://fhir.epic.com)

---

## Step 1 — Generate an RS384 Key Pair

```bash
make keys
```

This creates:
- `keys/private_key.pem` — stays on your machine, never shared
- `keys/public_key.pem` — registered with Epic

If you prefer manual:
```bash
mkdir -p keys
openssl genrsa -out keys/private_key.pem 2048
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem
```

> ⚠️ `keys/` is `.gitignore`d. Never commit private key files.

---

## Step 2 — Register a Backend App on Epic

1. Go to [fhir.epic.com](https://fhir.epic.com) → **Developer Apps** → **Create App**
2. Set **Application Audience** to `Backend Systems`
3. Under **SMART on FHIR Version**, select `SMART v2`
4. Paste the contents of `keys/public_key.pem` into the **Public Key** field
5. Under **API/Operation Access**, enable the following FHIR scopes:
   - `system/Patient.read`
   - `system/Condition.read`
   - `system/MedicationRequest.read`
   - `system/Observation.read`
   - `system/AllergyIntolerance.read`
   - `system/Encounter.read`
   - `system/DiagnosticReport.read`
6. Save — Epic provides a **Client ID**

---

## Step 3 — Configure `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```env
FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
SMART_TOKEN_URL=https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token
SMART_CLIENT_ID=<your-client-id-from-step-2>
SMART_PRIVATE_KEY_PATH=./keys/private_key.pem
```

---

## Step 4 — Run the Server

```bash
make run
```

Expected output:
```
INFO - EHR-MCP server starting...
INFO - Loaded SMART private key from keys/private_key.pem
INFO - MCP server running on stdio
```

---

## Step 5 — Test a Tool Call

Epic's sandbox includes test patients. Use Patient ID `eIXesllypH3M9tAA5WdJftQ3` (Camila Lopez — a commonly available test patient):

```python
# Quicktest — run from repo root with venv active
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test():
    async with MultiServerMCPClient({
        "ehr": {
            "command": "python",
            "args": ["-m", "ehr_mcp.server"],
            "transport": "stdio",
        }
    }) as client:
        tools = client.get_tools()
        get_context = next(t for t in tools if t.name == "get_patient_context")
        result = await get_context.ainvoke({"patient_id": "eIXesllypH3M9tAA5WdJftQ3"})
        print(result)

asyncio.run(test())
```

---

## Troubleshooting

| Error | Likely Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Wrong `SMART_CLIENT_ID` or key mismatch | Re-check Client ID; regenerate keys and re-register public key |
| `invalid_client` | JWT signed with wrong algorithm | Confirm Epic app is set to SMART v2 (RS384) |
| `Key not found` warning on startup | `SMART_PRIVATE_KEY_PATH` incorrect | Verify path relative to repo root; run `make keys` if not generated |
| Empty `ClinicalContextBundle` | Test patient has no resources | Try a different Epic sandbox Patient ID |
| `scope` error | Missing FHIR scopes in app registration | Add missing `system/*.read` scopes in Epic dev portal |

---

## Epic Sandbox Endpoints

| Endpoint | Value |
|---|---|
| FHIR Base URL | `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4` |
| Token URL | `https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token` |
| FHIR Metadata | `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/metadata` |
| Developer Portal | [fhir.epic.com](https://fhir.epic.com) |
