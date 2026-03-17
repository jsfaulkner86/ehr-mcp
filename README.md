**Inspired by: https://arxiv.org/abs/2509.15957**

**EHR-MCP**

A Framework-Agnostic Interoperability Protocol

for Multi-Agent Healthcare AI Systems

**Proposed Standard Specification — Draft 1.0**

March 2026

Status: Draft for Public Comment

# **Table of Contents**

# **1\. Executive Summary**

## **1.1 The Problem**

Healthcare AI is experiencing unprecedented growth, yet the industry faces a critical interoperability gap: AI agents operate in isolation. Individual agents may excel at clinical documentation, prior authorization, or care coordination, but they cannot communicate with each other or seamlessly bridge the disconnected systems that define healthcare’s operational reality—electronic health records (EHRs), payer platforms, and government regulatory systems.

## **1.2 The Solution**

EHR-MCP is a framework-agnostic middleware protocol that unifies agent-to-agent communication (drawing on A2A protocol patterns) with agent-to-system communication (via MCP) across the entire healthcare ecosystem. Any AI agent—regardless of its underlying framework (LangChain, AutoGen, CrewAI, or vendor-specific platforms like Epic’s Agent Factory)—can register, discover peers, negotiate capabilities, and exchange clinical and administrative data through a single, standards-based communication bus.

## **1.3 Why Now**

The convergence of several market forces creates a compelling window of opportunity. The Model Context Protocol (MCP), introduced by Anthropic in November 2024, is rapidly gaining traction in healthcare[^1]. Healthcare IT News identified 2026 as the year healthcare embraces MCP[^2], and HL7 has begun actively exploring how MCP and A2A can integrate with FHIR[^3]. TEFCA has scaled from 10 million to nearly 500 million records exchanged[^4], the CMS Prior Authorization Rule now mandates FHIR-based APIs, and Epic has launched its Agent Factory platform for no-code AI agent creation[^5].

## **1.4 Intended Audience & Adoption Path**

This specification is intended for a broad range of stakeholders across the healthcare ecosystem. The following organizations are encouraged to review, implement, and contribute to the EHR-MCP standard:

* **Health Systems & Provider Organizations:** Adopting organizations operating EHRs (Epic, Oracle Health, athenahealth, MEDITECH) that seek to enable multi-agent AI coordination across clinical and administrative workflows.

* **EHR Vendors:** Platform developers who can build native EHR-MCP adapters, enabling their agent ecosystems to interoperate with agents from other frameworks and organizations.

* **Payer Organizations:** Health plans and clearinghouses that can expose prior authorization, eligibility, and claims workflows through EHR-MCP-compliant interfaces.

* **Health Technology Companies:** AI agent developers, interoperability platform vendors, and clinical decision support providers who can implement EHR-MCP adapters for their products.

* **Government Agencies:** ONC, CMS, and state health departments that can align regulatory requirements with EHR-MCP conformance levels.

**How to engage:** Implementers MAY begin by deploying EHR-MCP adapters for their highest-priority use cases. Organizations interested in shaping the specification SHOULD participate in the EHR-MCP working group. EHR vendors and platform developers SHOULD contribute reference adapter implementations to accelerate ecosystem adoption.

# **2\. Problem Statement**

## **2.1 The Fragmented Agent Landscape**

Today’s healthcare AI ecosystem is a collection of capable but disconnected agents. A clinical documentation agent within the EHR cannot communicate with a prior authorization agent at the payer. A care coordination agent at one hospital cannot discover or negotiate with a specialist referral agent at another. Each agent is locked within its framework, its vendor ecosystem, and its data silo.

## **2.2 Three Disconnected Domains**

The problem manifests across three critical domains that define healthcare operations:

* **EHR Systems:** Epic, Oracle Health (Cerner), athenahealth, and MEDITECH each expose different APIs, data models, and integration patterns. Agents built for one system cannot easily operate with another.

* **Payer Systems:** Claims processing, prior authorization, eligibility verification, and remittance operate through EDI/X12 transaction sets (270/271, 278, 837, 835\) with legacy connectivity that most AI frameworks cannot natively consume.

* **Government & Regulatory Systems:** TEFCA/USCDI exchanges for national interoperability, CMS compliance reporting, public health registries, and quality measure submission each require specialized adapters and credentials.

## **2.3 What Is Missing**

The industry lacks a unified communication layer that enables agents from different frameworks, vendors, and organizations to: discover each other and advertise capabilities; negotiate which data and actions are available; exchange clinical and administrative data in standardized formats; and coordinate multi-step workflows across organizational boundaries.

## **2.4 The Impact**

Without such a layer, health systems experience duplicated work across departmental AI initiatives, manual handoffs that negate automation gains, inconsistent data quality across systems, slow prior authorization turnaround[^6], and care coordination gaps during transitions of care. As Deloitte has noted, agentic AI has the potential to transform consumer engagement, care delivery, and payment processes—but only if agents can break out of their silos[^7]. Oracle Health has similarly identified payer-provider friction as a key area where collaborative AI agents can drive efficiency[^8].

# **3\. Market Context & Regulatory Landscape**

## **3.1 The MCP Ecosystem**

The Model Context Protocol, released by Anthropic in November 2024, provides an open standard for connecting AI assistants to data sources using JSON-RPC[^9]. Several healthcare-specific implementations have emerged:

* **Innovaccer HMCP** (May 2025): A healthcare-specific MCP extension with native FHIR R4/R5 support, enterprise master patient index (EMPI), OAuth2 authentication, audit trails, PHI protection, and rate limiting[^10].

* **AWS HealthLake MCP Server** (January 2026): An open-source MCP server enabling natural language interfaces to FHIR CRUD operations within AWS HealthLake[^11].

* **Momentum FHIR MCP Server:** An open-source server providing LOINC code validation, semantic search, and full FHIR CRUD, compatible with any MCP client[^12].

* **Healthcare MCP Gateways:** Emerging security and governance layers (Innovaccer, Keragon) between AI agents and clinical systems, providing pre-built EHR connectors for Epic, Cerner, and athenahealth[^13].

## **3.2 The A2A Ecosystem**

Google’s Agent-to-Agent (A2A) protocol, launched in April 2025 and now housed at the Linux Foundation with 150+ supporting organizations, addresses the complementary challenge of agent-to-agent communication[^14]. Where MCP standardizes how agents connect to tools and data sources, A2A standardizes how agents discover, negotiate with, and delegate tasks to each other[^15]. Built on HTTP, SSE, and JSON-RPC, A2A introduces Agent Cards for discoverability, supports asynchronous long-running tasks, and uses enterprise-grade OAuth2 authentication[^16].

## **3.3 Regulatory Drivers**

* **TEFCA Growth:** The Trusted Exchange Framework and Common Agreement has scaled from approximately 10 million to nearly 500 million records exchanged in 2025, establishing national-scale infrastructure for interoperability[^17].

* **USCDI v7:** A draft released in January 2026 adds 29 new data elements, expanding the standardized clinical data set available through certified health IT.

* **CMS Prior Authorization Rule:** Effective January 2026, this mandate requires FHIR-based APIs for prior authorization, fundamentally changing payer-provider data exchange.

* **HTI-1:** Requires USCDI v3 via FHIR APIs, raising the baseline for certified EHR interoperability.

## **3.4 EHR Vendor AI Strategies**

Major EHR vendors are aggressively investing in AI. Epic’s Agent Factory provides a no-code platform for creating and monitoring AI agents, alongside its Art (clinician AI) and Penny (revenue cycle AI) solutions[^18]. Epic reports a 42% reduction in prior authorization submission time at Summit Health[^19]. Oracle Health has announced AI agents for payer-provider collaboration[^20]. Verily’s FHIR-AgentBench benchmark has demonstrated that FHIR-based agent Q\&A can improve from 50% to 80% accuracy with self-improvement techniques[^21].

## **3.5 Standards Convergence**

HL7 is actively exploring how MCP and A2A can integrate with FHIR, signaling that the standards bodies recognize the importance of agent communication protocols alongside traditional interoperability standards[^22]. Anthropic has released HIPAA-ready Claude with native FHIR development capabilities and prior authorization review skills[^23]. This convergence creates the foundation for a unified architecture.

# **4\. Architecture Overview**

The EHR-MCP architecture consists of four horizontal layers, each addressing a distinct concern in the healthcare agent communication stack. This section describes each layer from top (agent-facing) to bottom (system-facing).

| Layer | Function | Key Components |
| :---- | :---- | :---- |
| 1\. Agent Framework | Framework-agnostic interface | Agent Registration, Discovery, Capability Negotiation |
| 2\. EHR-MCP Bus | Unified message bus | Message Router, Context Manager, Session Manager, Event Bus |
| 3\. Protocol Adapters | Healthcare protocol translation | FHIR R4, EDI/X12, TEFCA/USCDI, HL7 v2 |
| 4\. System Endpoints | External system connectivity | EHR, Payer, Government, Registries |

## **4.1 Layer 1: Agent Framework Layer**

The topmost layer provides a framework-agnostic interface that allows any AI agent—regardless of its underlying technology—to participate in the EHR-MCP ecosystem. This includes agents built with LangChain, AutoGen, CrewAI, custom frameworks, and vendor-specific platforms such as Epic’s Agent Factory[^24].

### **Agent Registration & Discovery**

Agents publish Agent Cards (drawing on the A2A protocol pattern) that describe their capabilities, supported FHIR resources, clinical domains of expertise, and trust attestations[^25]. When an agent connects to an EHR-MCP bus, it registers its card with the discovery service, making it findable by other agents seeking specific capabilities (e.g., “prior authorization for orthopedic procedures” or “medication reconciliation for cardiology patients”).

### **Capability Negotiation**

When two agents establish a connection, they negotiate which protocol features, FHIR resources, and clinical domains are mutually available. This ensures that an agent requesting lab results, for example, connects only with agents or adapters capable of serving FHIR Observation resources with LOINC-coded values.

## **4.2 Layer 2: EHR-MCP Communication Bus**

The communication bus is the heart of the architecture—a unified message fabric that handles both agent-to-agent and agent-to-system communication patterns.

### **Agent-to-Agent Communication (A2A Patterns)**

Peer-to-peer communication between agents regardless of framework. An orchestrator agent can delegate sub-tasks to specialist agents, receive status updates, and aggregate results—all through the standardized bus. This draws on the A2A protocol’s patterns for task delegation, status updates, and result sharing[^26].

### **Agent-to-System Communication (MCP Patterns)**

Standardized tool and resource access to external healthcare systems. Agents invoke tools (e.g., “query patient medications” or “submit prior auth request”) through the MCP interface, and the bus routes these requests to the appropriate protocol adapter[^27].

### **Core Components**

* **Message Router:** Routes messages based on intent, capability matching, and authorization policies. Ensures that a prior authorization request reaches the EDI adapter while a medication query reaches the FHIR adapter.

* **Context Manager:** Maintains shared clinical context across agent interactions, including patient context, encounter context, and care plan context. Prevents redundant data fetches and ensures all agents in a workflow operate on consistent information.

* **Session Manager:** Supports both stateless and stateful interaction modes using MCP Streamable HTTP patterns. Short-lived queries use stateless sessions; complex multi-step workflows use stateful sessions with managed lifecycle.

* **Event Bus:** A publish/subscribe mechanism for real-time clinical events, including HL7 v2 ADT triggers (admission, discharge, transfer), order events, and result events. Agents subscribe to event types relevant to their function.

## **4.3 Layer 3: Healthcare Protocol Adapters**

The adapter layer translates between the unified EHR-MCP message format and the diverse protocols used across healthcare systems.

| Adapter | Capabilities |
| :---- | :---- |
| FHIR R4 | Full CRUD operations on FHIR resources, SMART on FHIR authorization, CDS Hooks integration, Bulk FHIR for population health queries |
| EDI/X12 | 270/271 (eligibility), 278 (prior auth), 837 (claims), 835 (remittance), 276/277 (claim status) |
| TEFCA/USCDI | QHIN-to-QHIN exchange, USCDI v3+ data element mapping, document exchange and FHIR API modes |
| HL7 v2 | ADT messages, ORM/OBR/OBX for orders and results (legacy system bridge) |

## **4.4 Layer 4: System Endpoints**

The bottom layer connects to the external systems that hold healthcare data and process transactions.

* **EHR Systems:** Epic (via FHIR R4, MyChart APIs), Oracle Health/Cerner, athenahealth, MEDITECH

* **Payer Systems:** Commercial payers, Medicare/Medicaid, clearinghouses

* **Government Systems:** TEFCA QHINs, state HIEs, CMS, FDA (future real-world data)

* **Clinical Registries:** Quality reporting systems, public health registries

# **5\. Security & Governance Architecture**

In a multi-agent healthcare system, security and governance are not features—they are foundational requirements. This specification defines defense-in-depth across all layers, drawing on established healthcare security models[^28].

## **5.1 Zero Trust Model**

Every agent-to-agent and agent-to-system call MUST be authenticated and authorized. No implicit trust SHALL be granted based on network location or prior interaction. Each request MUST carry verifiable credentials, and the communication bus SHALL validate them against current policies before routing.

## **5.2 Authentication & Authorization**

* **Transport Layer:** Implementations MUST use OAuth 2.0/2.1 for all transport-level authentication, consistent with MCP standards[^29].

* **Clinical Data Access:** SMART on FHIR scopes MUST control which clinical data each agent can access, at the resource and field level.

* **Agent Identity & Trust:** Agent certificates, capability attestation, and trust scoring ensure that only verified agents participate in workflows. Trust scores SHOULD be computed based on certification status, audit history, and organizational attestation.

## **5.3 PHI Protection**

* Encryption at rest (AES-256) and in transit (TLS 1.3) is REQUIRED for all implementations.

* Implementations SHOULD provide a de-identification pipeline for analytics and population health use cases.

* The minimum necessary principle MUST be enforced through SMART on FHIR scopes—agents receive only the data elements required for their task.

* HIPAA compliance by design: all PHI handling MUST conform to the HIPAA Security Rule and Privacy Rule.

## **5.4 Audit & Provenance**

Every agent action, data access event, and decision point MUST be logged with full provenance. Audit records SHALL capture the agent identity, timestamp, data accessed, action taken, clinical context, and outcome. This creates a complete, immutable chain of accountability for regulatory review and clinical quality assurance.

## **5.5 Governance Dashboard**

Implementations SHOULD provide a real-time governance dashboard for operational visibility into agent actions, data flows, and compliance status. Health system administrators can monitor active agents, review data access patterns, flag anomalies, and generate compliance reports without requiring engineering support.

# **6\. Key Use Cases**

The following use cases demonstrate how the EHR-MCP architecture enables multi-agent coordination across healthcare’s three core domains.

## **6.1 Intelligent Prior Authorization**

Prior authorization is one of the most resource-intensive processes in healthcare, involving manual data gathering, rule interpretation, and cross-system communication. Epic reports a 42% reduction in submission time with AI assistance[^30]—EHR-MCP extends this by coordinating multiple specialized agents:

1. A **Clinical Documentation Agent** within the EHR detects a procedure order requiring authorization.

2. EHR-MCP routes the event to a **Prior Auth Orchestrator Agent** via the event bus.

3. The Orchestrator delegates tasks: a **Data Gathering Agent** pulls clinical evidence via FHIR, a **Payer Rules Agent** checks coverage via EDI 270/271, and a **Packaging Agent** assembles the 278 request.

4. An **Observer/Verifier Agent** validates completeness against payer requirements[^31].

5. The request is submitted to the payer; status is monitored via 276/277.

6. All agents communicate through EHR-MCP regardless of framework.

## **6.2 Cross-System Care Coordination**

Care transitions are a leading source of adverse events. EHR-MCP enables seamless multi-system coordination:

7. A patient is discharged from Hospital A (Epic) with follow-up needed at Hospital B (Oracle Health/Cerner).

8. A **Discharge Agent** publishes a transition-of-care event on the EHR-MCP event bus.

9. A **Care Coordination Agent** at Hospital B discovers the event and negotiates data access.

10. The FHIR and TEFCA adapters pull the CCD/CCDA, medications, and care plan[^32].

11. A **Scheduling Agent** books the follow-up appointment.

12. A **Patient Notification Agent** confirms the plan with the patient.

## **6.3 Population Health & Digital Twin Integration**

This use case illustrates how EHR-MCP connects population health analytics to patient-level digital twin simulation infrastructure:

13. An **Analytics Agent** queries Bulk FHIR for cohort identification across a health system’s population.

14. A **Risk Stratification Agent** scores patients using clinical and social determinant data.

15. Results feed into patient-level digital twin platforms for simulation and prediction.

16. A **Care Gap Agent** identifies intervention opportunities across the cohort.

17. An **Outreach Agent** coordinates interventions across EHR and payer systems.

## **6.4 Government Reporting & Compliance**

Regulatory reporting is increasingly complex and time-sensitive:

18. A **Quality Reporting Agent** aggregates clinical quality measures via FHIR.

19. A **Regulatory Agent** validates submissions against current CMS requirements.

20. A **Submission Agent** transmits data via TEFCA/QHIN channels.

21. A **Compliance Monitor Agent** tracks submission status, flags issues, and generates audit trails.

# **7\. Technical Specifications**

| Specification | Detail |
| :---- | :---- |
| Transport Protocol | JSON-RPC 2.0 over Streamable HTTP (MCP standard) |
| Agent Discovery | Agent Cards (A2A pattern) with healthcare extensions: supported FHIR resources, clinical domains, HIPAA attestation |
| Data Format | FHIR R4 Bundles as primary payload; adapters for EDI/X12, HL7 v2, CDA |
| Terminology | SNOMED CT, LOINC, ICD-10-CM, CPT, RxNorm mapped through FHIR ValueSets |
| Authentication | OAuth 2.0/2.1 \+ SMART on FHIR scopes |
| Transport Security | TLS 1.3; mutual TLS (mTLS) for agent-to-agent communication |
| Scalability | Stateless design, horizontal scaling, event-driven architecture |
| Deployment | Cloud-native (any cloud); on-premise options for sovereign health systems |

## **7.1 Agent Card Schema (Healthcare Extension)**

Each agent MUST publish an Agent Card extending the A2A pattern with healthcare-specific fields:

* **agentId:** Globally unique identifier

* **capabilities:** Array of supported FHIR resource types and operations

* **clinicalDomains:** SNOMED-coded clinical specialties (e.g., cardiology, oncology)

* **hipaaAttestation:** Certification status, BAA reference, compliance level

* **trustScore:** Computed score based on certification, audit history, organizational endorsement

* **supportedProtocols:** Array of protocol versions supported (MCP, A2A, FHIR)

# **8\. Implementation Roadmap**

The following phased approach provides guidance for adopting organizations implementing the EHR-MCP specification. Timelines are indicative and will vary based on organizational readiness and scope.

| Phase | Timeline | Deliverables |
| :---- | :---- | :---- |
| Phase 1 | Months 1–3 | Core MCP communication layer \+ FHIR R4 adapter \+ 2-agent PoC (prior authorization use case) |
| Phase 2 | Months 4–6 | A2A agent discovery \+ EDI/X12 adapter \+ multi-agent orchestration \+ payer connectivity |
| Phase 3 | Months 7–9 | TEFCA/USCDI adapter \+ government system integration \+ governance dashboard |
| Phase 4 | Months 10–12 | Production hardening, EHR agent platform integration, digital twin platform integration |

## **8.1 Phase 1: Foundation (Months 1–3)**

Adopting organizations SHOULD begin by establishing the core EHR-MCP communication bus with JSON-RPC 2.0 over Streamable HTTP. This phase includes implementing the FHIR R4 adapter with SMART on FHIR authorization and building a two-agent proof of concept demonstrating the prior authorization use case end-to-end: a Clinical Documentation Agent detecting orders and a Prior Auth Agent assembling and submitting requests.

## **8.2 Phase 2: Multi-Agent Expansion (Months 4–6)**

Implementers SHOULD integrate A2A-pattern agent discovery with healthcare-extended Agent Cards. This phase includes building the EDI/X12 adapter for payer connectivity (270/271, 278\) and demonstrating multi-agent orchestration with the Orchestrator-Specialist-Observer pattern.

## **8.3 Phase 3: Government & Governance (Months 7–9)**

Organizations SHOULD implement the TEFCA/USCDI adapter for national interoperability, connect to QHIN networks for cross-organizational data exchange, and deploy the governance dashboard for real-time agent monitoring and compliance.

## **8.4 Phase 4: Production & Integration (Months 10–12)**

Production hardening with load testing, failover, and disaster recovery. Implementers SHOULD integrate with EHR vendor agent platforms (e.g., Epic Agent Factory) for native agent connectivity. This phase also includes digital twin platform integration, connecting population health agents to patient-level simulation infrastructure.

# **9\. Adoption & Ecosystem**

## **9.1 Relationship to Existing Standards**

EHR-MCP does not replace existing healthcare interoperability standards; it extends and unifies them within a multi-agent communication framework. The following table describes how EHR-MCP relates to the current standards landscape:

| Standard / Protocol | Scope | EHR-MCP Relationship |
| :---- | :---- | :---- |
| HMCP (Innovaccer) | Healthcare-specific MCP extension; FHIR R4/R5, EMPI, PHI protection | EHR-MCP incorporates HMCP’s healthcare MCP patterns and extends them with agent-to-agent coordination, EDI/X12, and TEFCA support |
| AWS HealthLake MCP | FHIR CRUD via MCP on AWS HealthLake | EHR-MCP is cloud-agnostic; HealthLake MCP servers can serve as one system endpoint within the EHR-MCP architecture |
| A2A (Google / Linux Foundation) | Agent-to-agent discovery, negotiation, task delegation | EHR-MCP adopts A2A patterns (Agent Cards, task delegation) and adds healthcare-specific extensions (FHIR resources, HIPAA attestation, clinical domains) |
| HL7 FHIR R4 | Healthcare data exchange standard | FHIR R4 is the primary data format within EHR-MCP; the FHIR adapter provides full CRUD, CDS Hooks, and Bulk FHIR |
| TEFCA / USCDI | National health data exchange framework | EHR-MCP’s TEFCA/USCDI adapter enables agents to participate in national-scale interoperability |
| SMART on FHIR | App authorization for FHIR | EHR-MCP REQUIRES SMART on FHIR scopes for all clinical data access control |
| X12 EDI | Administrative healthcare transactions | EHR-MCP’s EDI/X12 adapter translates between agent requests and legacy payer transaction formats |

Research from BCG has identified AI agents as transformative for precision medicine and workflow automation in healthcare[^33]. Peer-reviewed research in PMC has documented effective multiagent patterns for scheduling, routing, and summarization in clinical settings[^34]. A recent Frontiers analysis further supports the case for agentic AI frameworks in healthcare delivery[^35]. EHR-MCP provides the interoperability protocol that these multi-agent architectures require to operate across organizational and system boundaries.

## **9.2 Implementation Guidance**

Organizations can adopt EHR-MCP incrementally, starting with the components most relevant to their operational priorities:

* **Minimal viable adoption:** Deploy a single EHR-MCP adapter (e.g., FHIR R4) and register two agents to demonstrate cross-framework communication for one use case.

* **Departmental rollout:** Expand to multiple adapters (FHIR \+ EDI/X12) and deploy the prior authorization use case with 3–5 coordinating agents.

* **Enterprise adoption:** Deploy all four adapters, enable cross-organizational agent discovery via TEFCA, and implement the full governance dashboard.

Implementers SHOULD begin with read-only agent interactions before enabling write operations. All implementations MUST complete security and PHI protection requirements (Section 5\) before processing real patient data.

## **9.3 Governance & Specification Development**

This specification is proposed as the foundation for an open, community-governed standard. The following governance model is recommended:

* **Working Group:** An open working group, potentially under the auspices of HL7, ONC, or a similar standards body, SHOULD be established to maintain and evolve the specification.

* **Versioning:** The specification SHOULD follow semantic versioning (MAJOR.MINOR.PATCH) with public comment periods for major revisions.

* **Reference Implementations:** The working group SHOULD maintain open-source reference implementations of each protocol adapter to accelerate adoption.

* **Conformance Testing:** A conformance test suite SHOULD be developed to validate implementations against the specification (see Appendix C).

# **10\. Conclusion & Call for Participation**

The healthcare industry stands at an inflection point. AI agents are proliferating across clinical, administrative, and financial workflows, but without a unifying communication layer, they will remain isolated tools rather than a coordinated system of intelligence. EHR-MCP provides that layer: framework-agnostic, standards-based, and purpose-built for healthcare’s unique regulatory, security, and interoperability requirements.

This specification is published as a draft for public comment and industry input. Organizations interested in contributing to this specification are invited to participate through the following channels:

* **Review & Comment:** Submit feedback on this draft through the public comment process. All comments will be reviewed by the working group and addressed in subsequent revisions.

* **Pilot Implementation:** Organizations are encouraged to implement EHR-MCP adapters for their environments and share implementation experience reports.

* **Working Group Participation:** To participate in the EHR-MCP working group, organizations should express interest through the specification’s public repository. Active contributors will shape conformance requirements, adapter specifications, and governance policies.

* **Reference Adapter Development:** EHR vendors, payer platforms, and health technology companies are invited to contribute open-source adapter implementations for their systems.

# **Appendix A: Glossary**

| Term | Definition |
| :---- | :---- |
| A2A | Agent-to-Agent protocol; Google-originated standard for multi-agent communication, now at Linux Foundation |
| ADT | Admission, Discharge, Transfer; HL7 v2 message type for patient movement events |
| Agent Card | Structured metadata describing an agent’s capabilities, used for discovery and negotiation |
| CCD/CCDA | Continuity of Care Document; standardized clinical summary for care transitions |
| CDS Hooks | Clinical Decision Support Hooks; HL7 standard for EHR-integrated decision support |
| CMS | Centers for Medicare & Medicaid Services |
| EDI/X12 | Electronic Data Interchange; ANSI X12 standard for healthcare administrative transactions |
| EHR | Electronic Health Record |
| EMPI | Enterprise Master Patient Index; system for matching patient identities across systems |
| FHIR | Fast Healthcare Interoperability Resources; HL7 standard for healthcare data exchange |
| HIPAA | Health Insurance Portability and Accountability Act |
| HL7 | Health Level Seven International; standards organization for health informatics |
| HMCP | Healthcare MCP; Innovaccer’s healthcare-specific extension of MCP |
| HTI-1 | Health Data, Technology, and Interoperability Rule; ONC regulation for certified health IT |
| MCP | Model Context Protocol; Anthropic’s standard for connecting AI to data sources |
| mTLS | Mutual Transport Layer Security; bidirectional certificate-based authentication |
| PHI | Protected Health Information |
| QHIN | Qualified Health Information Network; TEFCA-designated exchange network |
| SMART on FHIR | Substitutable Medical Applications and Reusable Technologies; authorization framework for FHIR |
| TEFCA | Trusted Exchange Framework and Common Agreement; national health data exchange framework |
| USCDI | United States Core Data for Interoperability; standardized clinical data set |

# **Appendix B: Standards Reference**

| Standard | Purpose | Reference |
| :---- | :---- | :---- |
| HL7 FHIR R4 | Core healthcare data exchange | hl7.org/fhir/R4 |
| SMART on FHIR | Application authorization | smarthealthit.org |
| CDS Hooks | Clinical decision support | cds-hooks.hl7.org |
| HL7 v2 | Legacy message exchange | hl7.org |
| TEFCA | National interoperability framework | healthit.gov/tefca |
| USCDI | Core clinical data set | healthit.gov/uscdi |
| X12 EDI | Administrative transactions | x12.org |
| SNOMED CT | Clinical terminology | snomed.org |
| LOINC | Lab/observation codes | loinc.org |
| ICD-10-CM | Diagnosis codes | cms.gov |
| CPT | Procedure codes | ama-assn.org |
| RxNorm | Medication terminology | nlm.nih.gov/rxnorm |
| OAuth 2.0/2.1 | Authentication protocol | oauth.net |
| JSON-RPC 2.0 | Remote procedure call protocol | jsonrpc.org |
| MCP | Model Context Protocol | modelcontextprotocol.io |
| A2A | Agent-to-Agent protocol | github.com/google/A2A |

# **Appendix C: Conformance Requirements**

This appendix defines conformance levels for implementations of the EHR-MCP specification. The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in RFC 2119\.

## **C.1 Conformance Levels**

Two conformance levels are defined:

* **EHR-MCP Compliant:** Full conformance. Implementations at this level support the complete specification and can participate in all EHR-MCP workflows.

* **EHR-MCP Compatible:** Partial conformance. Implementations at this level support a subset of the specification sufficient for basic agent communication and at least one protocol adapter.

## **C.2 EHR-MCP Compatible (Minimum Requirements)**

An implementation claiming EHR-MCP Compatible status MUST satisfy all of the following requirements:

1. MUST implement JSON-RPC 2.0 over Streamable HTTP as the transport protocol.

2. MUST support Agent Card publication and discovery with at minimum the agentId, capabilities, and supportedProtocols fields.

3. MUST implement at least one protocol adapter (FHIR R4, EDI/X12, TEFCA/USCDI, or HL7 v2).

4. MUST implement OAuth 2.0/2.1 for transport-level authentication.

5. MUST encrypt all data in transit using TLS 1.3.

6. MUST log all agent actions with agent identity, timestamp, and action taken.

7. SHOULD implement SMART on FHIR scopes for clinical data access control.

8. SHOULD support the Context Manager for shared clinical context.

## **C.3 EHR-MCP Compliant (Full Requirements)**

An implementation claiming EHR-MCP Compliant status MUST satisfy all EHR-MCP Compatible requirements AND the following additional requirements:

1. MUST implement the FHIR R4 adapter with SMART on FHIR authorization.

2. MUST support agent-to-agent communication using A2A patterns (task delegation, status updates, result sharing).

3. MUST implement capability negotiation between agents.

4. MUST implement the full Agent Card schema including clinicalDomains, hipaaAttestation, and trustScore fields.

5. MUST implement the Context Manager for shared clinical context across agent interactions.

6. MUST implement the Event Bus for publish/subscribe clinical event handling.

7. MUST implement mutual TLS (mTLS) for agent-to-agent communication.

8. MUST provide full audit provenance including clinical context and outcome for every agent action.

9. MUST enforce the minimum necessary principle for PHI access through SMART on FHIR scopes.

10. SHOULD implement at least two protocol adapters.

11. SHOULD provide a governance dashboard for real-time agent monitoring.

12. MAY implement the digital twin integration interface for population health use cases.

## **C.4 Conformance Assertion**

Implementations asserting conformance to this specification MUST publish a conformance statement identifying:

* The conformance level claimed (Compatible or Compliant).

* The version of the EHR-MCP specification implemented.

* The protocol adapters implemented.

* Any optional features supported.

* The results of conformance testing, if available.

[^1]: Anthropic, "Model Context Protocol," November 2024\. [https://www.anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)

[^2]: Healthcare IT News, "How Health Systems Can Prepare for the Next Phase of AI Adoption," December 2025\. [https://www.healthcareitnews.com/news/how-health-systems-can-prepare-next-phase-ai-adoption](https://www.healthcareitnews.com/news/how-health-systems-can-prepare-next-phase-ai-adoption)

[^3]: HL7 Blog, "Building the Standards Infrastructure for Healthcare AI," November 2025\. [https://blog.hl7.org/building-the-standards-infrastructure-for-healthcare-ai-lessons-from-the-interoperability-journey](https://blog.hl7.org/building-the-standards-infrastructure-for-healthcare-ai-lessons-from-the-interoperability-journey)

[^4]: HHS/ONC, "TEFCA Reaches Nearly 500 Million Health Records Exchanged," February 2026\. [https://healthit.gov/news/tefca-americas-national-interoperability-network-reaches-nearly-500-million-health-records-exchanged-as-hhs-leverages-technology-and-ai-to-lower-costs-and-reduce-burden/](https://healthit.gov/news/tefca-americas-national-interoperability-network-reaches-nearly-500-million-health-records-exchanged-as-hhs-leverages-technology-and-ai-to-lower-costs-and-reduce-burden/)

[^5]: Healthcare IT News, "HIMSS26: Epic Highlights No-Code Agent Factory and Other AI Advances," 2026\. [https://www.healthcareitnews.com/news/himss26-epic-highlight-no-code-agent-factory-and-other-ai-advances](https://www.healthcareitnews.com/news/himss26-epic-highlight-no-code-agent-factory-and-other-ai-advances)

[^6]: Oracle News, "Oracle Health to Enable Accelerated Payer-Provider Collaboration," September 2025\. [https://www.oracle.com/news/announcement/oracle-health-to-enable-accelerated-payer-provider-collaboration-2025-09-11/](https://www.oracle.com/news/announcement/oracle-health-to-enable-accelerated-payer-provider-collaboration-2025-09-11/)

[^7]: Deloitte Insights, "Agentic AI: Health Care Operating Model Change," 2025\. [https://www.deloitte.com/us/en/insights/industry/health-care/agentic-ai-health-care-operating-model-change.html](https://www.deloitte.com/us/en/insights/industry/health-care/agentic-ai-health-care-operating-model-change.html)

[^8]: Oracle News, "Oracle Health to Enable Accelerated Payer-Provider Collaboration," September 2025\. [https://www.oracle.com/news/announcement/oracle-health-to-enable-accelerated-payer-provider-collaboration-2025-09-11/](https://www.oracle.com/news/announcement/oracle-health-to-enable-accelerated-payer-provider-collaboration-2025-09-11/)

[^9]: Anthropic, "Model Context Protocol," November 2024\. [https://www.anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)

[^10]: Innovaccer, "Introducing HMCP: A Universal Open Standard for AI in Healthcare," May 2025\. [https://innovaccer.com/blogs/introducing-hmcp-a-universal-open-standard-for-ai-in-healthcare](https://innovaccer.com/blogs/introducing-hmcp-a-universal-open-standard-for-ai-in-healthcare)

[^11]: AWS Industries Blog, "Building Healthcare AI Agents with Open Source AWS HealthLake MCP Server," January 2026\. [https://aws.amazon.com/blogs/industries/building-healthcare-ai-agents-with-open-source-aws-healthlake-mcp-server/](https://aws.amazon.com/blogs/industries/building-healthcare-ai-agents-with-open-source-aws-healthlake-mcp-server/)

[^12]: The Momentum, "Introducing FHIR MCP Server," 2025\. [https://www.themomentum.ai/blog/introducing-fhir-mcp-server-natural-language-interface-for-healthcare-data](https://www.themomentum.ai/blog/introducing-fhir-mcp-server-natural-language-interface-for-healthcare-data)

[^13]: MintMCP, "Gateways: Healthcare Organizations with MCP," February 2026\. [https://www.mintmcp.com/blog/gateways-healthcare-organizations-with-mcp](https://www.mintmcp.com/blog/gateways-healthcare-organizations-with-mcp)

[^14]: Google Developers Blog, "A2A: A New Era of Agent Interoperability," April 2025\. [https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)

[^15]: IBM, "Agent2Agent Protocol," 2025\. [https://www.ibm.com/think/topics/agent2agent-protocol](https://www.ibm.com/think/topics/agent2agent-protocol)

[^16]: Google Cloud Blog, "Agent2Agent Protocol Is Getting an Upgrade," 2025\. [https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade)

[^17]: HHS/ONC, "TEFCA Reaches Nearly 500 Million Health Records Exchanged," February 2026\. [https://healthit.gov/news/tefca-americas-national-interoperability-network-reaches-nearly-500-million-health-records-exchanged-as-hhs-leverages-technology-and-ai-to-lower-costs-and-reduce-burden/](https://healthit.gov/news/tefca-americas-national-interoperability-network-reaches-nearly-500-million-health-records-exchanged-as-hhs-leverages-technology-and-ai-to-lower-costs-and-reduce-burden/)

[^18]: Healthcare IT News, "HIMSS26: Epic Highlights No-Code Agent Factory and Other AI Advances," 2026\. [https://www.healthcareitnews.com/news/himss26-epic-highlight-no-code-agent-factory-and-other-ai-advances](https://www.healthcareitnews.com/news/himss26-epic-highlight-no-code-agent-factory-and-other-ai-advances)

[^19]: Epic, "Real Results, Right Now: How Epic AI Is Reducing Costs, Improving Care, and Helping Patients," 2026\. [https://www.epic.com/epic/post/real-results-right-now-how-epic-ai-is-reducing-costs-improving-care-and-helping-patients/](https://www.epic.com/epic/post/real-results-right-now-how-epic-ai-is-reducing-costs-improving-care-and-helping-patients/)

[^20]: Oracle News, "Oracle Health to Enable Accelerated Payer-Provider Collaboration," September 2025\. [https://www.oracle.com/news/announcement/oracle-health-to-enable-accelerated-payer-provider-collaboration-2025-09-11/](https://www.oracle.com/news/announcement/oracle-health-to-enable-accelerated-payer-provider-collaboration-2025-09-11/)

[^21]: Verily, "Introducing FHIR-AgentBench," 2025\. [https://verily.com/perspectives/Introducing-FHIR-AgentBench](https://verily.com/perspectives/Introducing-FHIR-AgentBench)

[^22]: HL7 Blog, "Building the Standards Infrastructure for Healthcare AI," November 2025\. [https://blog.hl7.org/building-the-standards-infrastructure-for-healthcare-ai-lessons-from-the-interoperability-journey](https://blog.hl7.org/building-the-standards-infrastructure-for-healthcare-ai-lessons-from-the-interoperability-journey)

[^23]: Anthropic, "Healthcare & Life Sciences," January 2026\. [https://www.anthropic.com/news/healthcare-life-sciences](https://www.anthropic.com/news/healthcare-life-sciences)

[^24]: Healthcare IT News, "HIMSS26: Epic Highlights No-Code Agent Factory and Other AI Advances," 2026\. [https://www.healthcareitnews.com/news/himss26-epic-highlight-no-code-agent-factory-and-other-ai-advances](https://www.healthcareitnews.com/news/himss26-epic-highlight-no-code-agent-factory-and-other-ai-advances)

[^25]: Google Developers Blog, "A2A: A New Era of Agent Interoperability," April 2025\. [https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)

[^26]: Google Developers Blog, "A2A: A New Era of Agent Interoperability," April 2025\. [https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)

[^27]: Anthropic, "Model Context Protocol," November 2024\. [https://www.anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)

[^28]: Innovaccer, "Introducing HMCP: A Universal Open Standard for AI in Healthcare," May 2025\. [https://innovaccer.com/blogs/introducing-hmcp-a-universal-open-standard-for-ai-in-healthcare](https://innovaccer.com/blogs/introducing-hmcp-a-universal-open-standard-for-ai-in-healthcare)

[^29]: Anthropic, "Model Context Protocol," November 2024\. [https://www.anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)

[^30]: Epic, "Real Results, Right Now: How Epic AI Is Reducing Costs, Improving Care, and Helping Patients," 2026\. [https://www.epic.com/epic/post/real-results-right-now-how-epic-ai-is-reducing-costs-improving-care-and-helping-patients/](https://www.epic.com/epic/post/real-results-right-now-how-epic-ai-is-reducing-costs-improving-care-and-helping-patients/)

[^31]: TATEEDA, "Multi-Agent AI in Healthcare," 2025\. [https://tateeda.com/blog/multi-agent-ai-in-healthcare](https://tateeda.com/blog/multi-agent-ai-in-healthcare)

[^32]: HHS/ONC, "TEFCA Reaches Nearly 500 Million Health Records Exchanged," February 2026\. [https://healthit.gov/news/tefca-americas-national-interoperability-network-reaches-nearly-500-million-health-records-exchanged-as-hhs-leverages-technology-and-ai-to-lower-costs-and-reduce-burden/](https://healthit.gov/news/tefca-americas-national-interoperability-network-reaches-nearly-500-million-health-records-exchanged-as-hhs-leverages-technology-and-ai-to-lower-costs-and-reduce-burden/)

[^33]: BCG, "How AI Agents Will Transform Health Care," 2026\. [https://www.bcg.com/publications/2026/how-ai-agents-will-transform-health-care](https://www.bcg.com/publications/2026/how-ai-agents-will-transform-health-care)

[^34]: PMC, "Multiagent AI in Healthcare," 2025\. [https://pmc.ncbi.nlm.nih.gov/articles/PMC12360800/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12360800/)

[^35]: Frontiers, "Agentic AI in Healthcare," 2026\. [https://pmc.ncbi.nlm.nih.gov/articles/PMC12890637/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12890637/)
