# Disclaimer

**EHR-MCP: Framework-Agnostic EHR Interoperability Protocol**  
The Faulkner Group | Version 0.1.0

---

## Not a Medical Device

This software is a **developer infrastructure library and integration protocol**. It is not a cleared or approved medical device under FDA 21 CFR Part 820, ISO 13485, or any other medical device regulatory framework. It has not been submitted to or reviewed by the U.S. Food and Drug Administration (FDA) or any other regulatory authority.

EHR-MCP is designed to provide authenticated FHIR R4 data access for AI agent development and research purposes. It is not intended to serve as a clinical decision support tool, diagnostic aid, or patient safety system in its current form.

---

## Not Legal or Compliance Advice

Any references to HIPAA, SMART on FHIR, ONC HTI-1, or other regulatory frameworks in this repository are for **architectural and informational reference only**. They do not constitute legal advice, compliance certification, or a guarantee that any system built using this library will satisfy applicable legal or regulatory requirements.

You are solely responsible for ensuring that any system you build, deploy, or operate using EHR-MCP complies with all applicable laws, regulations, and standards in your jurisdiction. Consult qualified legal counsel and compliance professionals before deploying in a regulated healthcare environment.

---

## PHI and HIPAA

EHR-MCP is designed with HIPAA-aligned patterns (structured logging, PHI field masking, authenticated transport), but **does not by itself make any system HIPAA-compliant**. Organizations deploying systems that access or process Protected Health Information (PHI) must:

- Conduct an independent HIPAA risk analysis
- Execute appropriate Business Associate Agreements (BAAs) with all relevant vendors
- Implement the full set of required Administrative, Physical, and Technical Safeguards
- Validate compliance with a qualified HIPAA compliance professional

The Faulkner Group assumes no liability for PHI exposure, data breaches, or regulatory violations arising from the use of this library.

---

## No Warranty

This software is provided **"as is"**, without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement. In no event shall the authors or The Faulkner Group be liable for any claim, damages, or other liability — including but not limited to patient harm, data loss, or regulatory penalties — arising from the use of this software.

See the [MIT License](./LICENSE) for the full terms.

---

## Production Deployment

Before deploying EHR-MCP in a production environment that accesses live patient data, you **must**:

- Complete Epic (or applicable EHR vendor) production app registration and review
- Conduct an independent security review of your full system architecture
- Ensure all FHIR API calls occur over TLS 1.2+ and that private keys are stored securely
- Implement PHI-safe logging — do not log raw FHIR resources containing patient identifiers
- Route agent output through appropriate clinical guardrails before presenting to clinicians
- Establish monitoring, alerting, and incident response procedures

---

*The Faulkner Group provides healthcare IT architecture advisory services. For production deployment guidance, contact [john@thefaulknergroupadvisors.com](mailto:john@thefaulknergroupadvisors.com).*
