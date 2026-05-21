# Security Policy

> **Project:** EHR-MCP — Model Context Protocol Server for Electronic Health Records  
> **Maintainer:** The Faulkner Group  
> **Effective Date:** 2026-05-20  
> **Scope:** All code, configurations, MCP tool definitions, FHIR adapters, Epic integrations, and data schemas in this repository.

---

## ⚠️ Healthcare & PHI Notice

This project provides **direct MCP-layer access to EHR systems** including Epic and FHIR R4/R5 APIs. It is designed for use in women's health clinical environments and **must be treated as PHI-adjacent infrastructure at all times**.

- **Do not include real patient data, PHI, or PII in any issue, pull request, commit, or bug report.**
- All reproduction steps, logs, and payloads in vulnerability reports must use **synthetic or de-identified data only**.
- Any vulnerability that creates a pathway to PHI exposure is automatically a **Critical severity** finding and triggers HIPAA breach assessment.
- Contributors and researchers are responsible for ensuring their test environments use only synthetic FHIR resources.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` branch (latest) | ✅ Active |
| Tagged releases (`v1.x`) | ✅ Patch support for 12 months post-release |
| All prior versions | ❌ No longer supported |

---

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

### Preferred Channel

Use **GitHub's private Security Advisory** feature:

1. Navigate to the [Security tab](https://github.com/jsfaulkner86/ehr-mcp/security/advisories/new).
2. Click **"Report a vulnerability"**.
3. Complete the advisory form using the template below.

### Backup Channel

```
security@thefaulknergroupadvisors.com
```

Encrypt sensitive disclosures with the maintainer's GPG key (published at `https://thefaulknergroupadvisors.com/.well-known/security.txt`).

---

## Response SLA

| Severity | Initial Acknowledgment | Triage Complete | Target Patch |
|----------|----------------------|-----------------|--------------|
| Critical (CVSS ≥ 9.0 or PHI exposure) | 24 hours | 48 hours | 7 days |
| High (CVSS 7.0–8.9) | 48 hours | 5 business days | 30 days |
| Medium (CVSS 4.0–6.9) | 5 business days | 10 business days | 60 days |
| Low (CVSS < 4.0) | 10 business days | 20 business days | Next release cycle |

**Any vulnerability with a PHI exposure path is automatically Critical**, regardless of CVSS score.

---

## Vulnerability Report Template

```
### Summary
[One-paragraph description of the vulnerability]

### Affected Component
[ ] MCP tool definitions     [ ] FHIR adapter / client
[ ] Epic integration layer   [ ] Auth / token handling
[ ] .mcp.json config         [ ] Docker / deployment config
[ ] Dependency (name + CVE)

### Severity Estimate
CVSS Score (if known): ___
PHI Exposure Risk: [ ] Yes  [ ] No  [ ] Unknown
EHR Write Access Risk: [ ] Yes  [ ] No  [ ] Unknown

### Steps to Reproduce
1.
2.
3.

### Proof of Concept
[Code snippet, curl, or description — use synthetic FHIR resources ONLY, no real PHI]

### Suggested Fix (optional)

### Environment
- Python version:
- Docker version (if applicable):
- EHR target (Epic sandbox / local HAPI / other):
- Dependency snapshot (pyproject.toml or requirements.txt):
```

---

## Scope

### In Scope

- **MCP tool injection** — malformed inputs that manipulate EHR reads/writes through the MCP tool layer
- **FHIR resource authorization bypass** — accessing patient resources beyond the granted SMART on FHIR scopes
- **Token/credential leakage** — Epic OAuth tokens, FHIR client secrets, or API keys exposed in logs, environment files, or responses
- **PHI leakage via LLM context** — patient data persisting in agent scratchpads, conversation history, or external logs
- **Unauthorized EHR write access** — any path that allows write operations to clinical resources without explicit authorization
- **Docker container escape or privilege escalation** in the containerized deployment
- **Dependency CVEs** with exploitable attack surfaces in this EHR context
- **`.mcp.json` configuration injection** — malicious config that redirects MCP tool calls to unauthorized endpoints

### Out of Scope

- Vulnerabilities in Epic's own infrastructure — report via Epic's security program
- Vulnerabilities in upstream LLM providers (OpenAI, Anthropic) — report directly to those vendors
- Social engineering attacks against The Faulkner Group staff
- Theoretical vulnerabilities without a realistic attack path
- Issues in forked or derivative works not maintained by this repository

---

## Security Design Principles

Reports demonstrating a violation of these invariants are treated as high priority:

1. **Read-only by default** — MCP tools default to read-only FHIR access; write-capable tools require explicit scope grants and are disabled in sandbox mode.
2. **No PHI in LLM context by default** — patient identifiers must be tokenized before entering any model context window.
3. **Token isolation** — Epic OAuth tokens and FHIR credentials are never logged, never passed to model context, and scoped per-session.
4. **Audit trail on all EHR operations** — every FHIR read and write is logged with a request ID, user context, and timestamp.
5. **Sandbox / production isolation** — sandbox and production Epic environments must never share credentials or connection configs.

---

## Coordinated Disclosure Policy

- The Faulkner Group follows a **90-day coordinated disclosure** window from initial report to public advisory.
- Reporters who follow this policy in good faith will be credited (with consent) and are protected from legal action related to good-faith research.
- Active exploitation in the wild may accelerate the disclosure timeline.

---

## Dependency & Supply Chain Security

- Dependencies are pinned in `pyproject.toml` and `requirements.txt`.
- Maintainers run `pip-audit` and `safety check` before every release tag.
- GitHub Dependabot alerts are enabled.
- New dependencies require documented rationale in the PR description.
- Docker base images are pinned to digest hashes in production builds.

---

## Secret Scanning & CI Enforcement

- GitHub Secret Scanning is enabled on this repository.
- `.env` files are gitignored; `.env.example` is the only committed config template.
- Any committed secret (even in a branch) must be rotated immediately.
- Pre-commit hooks enforce `detect-secrets` scanning before remote push.

---

## Contact

| Role | Contact |
|------|---------|
| Security Disclosure | security@thefaulknergroupadvisors.com |
| General Maintainer | John Faulkner — github.com/jsfaulkner86 |
| Organization | [The Faulkner Group](https://thefaulknergroupadvisors.com) |

---

*This policy is reviewed quarterly and updated with each major release. Last reviewed: 2026-05-20.*
