# What Is EHR-MCP?

> A plain-language explanation for clinicians, health system leaders, and anyone who isn't a software engineer.

---

## The Problem It Solves

Healthcare AI is advancing fast. Health systems are deploying AI agents that can automate prior authorizations, triage patient messages, flag clinical risks, and assist with documentation.

But there's a fundamental plumbing problem:

**Every AI agent has to be individually wired to the EHR.**

If a hospital uses Epic, their developers build an Epic connector. If they switch to Oracle Health (Cerner), they rebuild it. If they want to use a different AI framework next year — LangChain today, something newer tomorrow — they rebuild it again.

That means massive duplicated effort, inconsistent data handling, and a system that breaks every time something changes.

---

## What EHR-MCP Does

EHR-MCP is a **universal translator layer** that sits between AI agents and the EHR.

Instead of each agent learning how to speak "Epic" or "Cerner," every agent speaks **EHR-MCP**. EHR-MCP handles the translation to whatever EHR is actually running underneath.

Think of it like a universal power adapter for international travel. You don't rewire your laptop for every country — you just plug into the adapter.

```
┌─────────────────────┐
│   AI Agents         │  ← LangChain, CrewAI, LangGraph, AutoGen, or any future framework
│  (any framework)    │
└────────┬────────────┘
         │  speaks EHR-MCP (one standard protocol)
         ▼
┌─────────────────────┐
│     EHR-MCP         │  ← This project
│  Protocol Layer     │
└────────┬────────────┘
         │  speaks FHIR R4 (the healthcare data standard)
         ▼
┌─────────────────────┐
│   Any EHR Vendor    │  ← Epic, Oracle Health, Meditech, or any FHIR R4 server
└─────────────────────┘
```

---

## What Is FHIR?

FHIR (Fast Healthcare Interoperability Resources) is the current federal standard for how healthcare data is shared electronically. Think of it as a universal language that modern EHRs are required to speak. EHR-MCP is built on FHIR R4, the most widely deployed version.

---

## What Is MCP?

MCP (Model Context Protocol) is an open standard created by Anthropic that defines how AI agents request and receive information from external systems. It is to AI agents what USB-C is to devices — a standard connector that works regardless of what's on either end.

---

## What Can an Agent Do With EHR-MCP?

Once an AI agent is connected to EHR-MCP, it can:

- **Retrieve a patient's full clinical context** — demographics, diagnoses, medications, allergies, labs, and encounter history — in a single request
- **Look up specific clinical data** — just medications, just lab results, just active conditions
- **Work across any EHR vendor** — the agent doesn't need to know whether the hospital runs Epic or Cerner
- **Feed that data directly into automated workflows** — prior auth, clinical triage, documentation, risk scoring

---

## Who Built This and Why?

EHR-MCP was designed by [John Faulkner](https://linkedin.com/in/johnathonfaulkner), Agentic AI Architect and founder of [The Faulkner Group](https://thefaulknergroupadvisors.com).

John spent 14 years building and implementing Epic EHR systems across 12 enterprise health systems. He watched the same integration problems get rebuilt from scratch at every organization, by every team, for every new tool.

EHR-MCP is the protocol he wished existed. It is open-source so that the whole healthcare AI ecosystem benefits — not just one vendor or one health system.

---

## Is This HIPAA Compliant?

EHR-MCP is a protocol, not a hosted service. HIPAA compliance depends on how it is deployed. The protocol is designed with compliance in mind:

- Authentication uses **SMART-on-FHIR Backend Services** — the healthcare industry standard for system-to-system access
- No patient data is stored by the protocol layer itself
- Access is scoped to only the resources the agent needs
- All data requests are authenticated and logged

Any production deployment should be reviewed by your organization's privacy and security team.

---

## Want to Learn More?

| Resource | Link |
|---|---|
| Full technical documentation | [README.md](./README.md) |
| How to contribute | [CONTRIBUTING.md](./CONTRIBUTING.md) |
| The Faulkner Group | [thefaulknergroupadvisors.com](https://thefaulknergroupadvisors.com) |
| LinkedIn | [linkedin.com/in/johnathonfaulkner](https://linkedin.com/in/johnathonfaulkner) |
