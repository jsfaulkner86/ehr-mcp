# Contributing to EHR-MCP

Thank you for your interest in contributing. EHR-MCP is an open protocol — the goal is to make it easier for any healthcare AI system to talk to any EHR. Contributions that advance that mission are welcome.

---

## What We're Building

EHR-MCP is a **vendor-agnostic interoperability protocol** built on Anthropic's Model Context Protocol (MCP) and FHIR R4. It gives AI agents a clean, standardized way to read clinical data from any conformant EHR — Epic, Cerner, Oracle Health, Meditech, or any FHIR R4 server.

The project is maintained by [John Faulkner](https://linkedin.com/in/johnathonfaulkner) and [The Faulkner Group](https://thefaulknergroupadvisors.com).

---

## Ways to Contribute

- **New FHIR resource support** — Add tools for resources not yet covered (e.g. CarePlan, ServiceRequest, ImagingStudy)
- **Vendor-specific adapters** — Document or handle quirks of specific EHR FHIR implementations
- **New agent framework examples** — LangGraph, AutoGen, Semantic Kernel, or others
- **Test coverage** — Unit tests against HAPI FHIR sandbox responses
- **Documentation** — Improve clarity, fix errors, add examples
- **Bug reports** — Open an issue with reproduction steps

---

## Getting Started

```bash
git clone https://github.com/jsfaulkner86/ehr-mcp
cd ehr-mcp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

For local testing without a real EHR, point `FHIR_BASE_URL` at the public HAPI FHIR R4 sandbox:

```
FHIR_BASE_URL=https://hapi.fhir.org/baseR4
```

The HAPI sandbox does not require authentication, so you can test FHIR resource retrieval without SMART credentials.

---

## Generating a SMART Private Key (for real EHR testing)

```bash
mkdir keys
openssl genrsa -out keys/private_key.pem 2048
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem
```

Register the **public key** with your EHR vendor's developer portal. Never commit `keys/` — it is in `.gitignore`.

---

## Contribution Guidelines

- **One concern per PR** — keep pull requests focused
- **No PHI in commits** — use synthetic or de-identified data only in tests and examples
- **Follow existing patterns** — new FHIR tools belong in `fhir_client.py` + `server.py`; new schemas in `schemas.py`
- **Document the clinical context** — if you add a new resource or tool, explain in plain language what clinical problem it solves
- **HIPAA awareness** — if your contribution touches data handling, note any compliance considerations in the PR description

---

## Opening an Issue

Use GitHub Issues for:
- Bug reports (include steps to reproduce and your FHIR server type if known)
- Feature requests (describe the clinical use case, not just the technical ask)
- Questions about the protocol design

---

## Code of Conduct

This project exists to improve healthcare. Contributions should reflect that mission. Be respectful, be precise, and remember that real patients and clinicians depend on software like this working correctly.
