# EHR-MCP

> **Framework-Agnostic Interoperability Protocol** — The connective tissue for multi-agent healthcare AI systems

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![FHIR](https://img.shields.io/badge/FHIR-R4-orange?style=flat-square)]()
[![Interoperability](https://img.shields.io/badge/Interoperability-Protocol-blue?style=flat-square)]()
[![Healthcare AI](https://img.shields.io/badge/Healthcare-AI-red?style=flat-square)]()

## The Problem

Multi-agent healthcare AI systems can't reach their potential if each agent speaks a different language. EHR data is siloed, agent frameworks are fragmented, and there's no standard protocol for how AI agents should communicate with clinical systems. EHR-MCP solves the interoperability layer.

## What It Does

A framework-agnostic Model Context Protocol (MCP) implementation for healthcare AI that:
- Defines a standard message schema for agent-to-EHR communication
- Abstracts FHIR R4 resource access behind a clean agent interface
- Works with any agent framework: LangChain, CrewAI, LangGraph, AutoGen
- Provides context packaging for patient data, clinical events, and workflow state

## Tech Stack

| Layer | Technology |
|---|---|
| Protocol | Model Context Protocol (MCP) |
| Healthcare Standard | FHIR R4 |
| Language | Python 3.11+ |
| Compatibility | LangChain, CrewAI, LangGraph, AutoGen |

## Getting Started

```bash
git clone https://github.com/jsfaulkner86/ehr-mcp
cd ehr-mcp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Environment Variables

```
OPENAI_API_KEY=your_key_here
FHIR_BASE_URL=your_fhir_endpoint
SMART_TOKEN_URL=your_smart_token_endpoint
SMART_CLIENT_ID=your_client_id
SMART_PRIVATE_KEY_PATH=./keys/private_key.pem
```

## Background

Built by [John Faulkner](https://linkedin.com/in/johnathonfaulkner), Agentic AI Architect and founder of [The Faulkner Group](https://thefaulknergroupadvisors.com). Designed from the interoperability gaps observed across 12 Epic enterprise health system implementations.

This implementation was inspired by the academic research of Masayoshi et al. (2025), who demonstrated that LLMs connected to EHR databases via MCP can autonomously retrieve clinically relevant information in real hospital settings with near-perfect accuracy on standard tasks. See [Academic Inspiration](#academic-inspiration) below.

## What's Next
- Epic FHIR sandbox integration
- Bidirectional write support for clinical workflow agents
- OpenAPI spec for third-party agent integration
- Reasoning and clinical impact assessment layer (per Masayoshi et al. future work)

---

## Academic Inspiration

This project was inspired by and builds upon the research framework described in:

> **EHR-MCP: Real-world Evaluation of Clinical Information Retrieval by Large Language Models via Model Context Protocol**
> Kanato Masayoshi, Masahiro Hashimoto, Ryoichi Yokoyama, Naoki Toda, Yoshifumi Uwamino, Shogo Fukuda, Ho Namkoong, Masahiro Jinzaki
> *arXiv:2509.15957 [cs.AI] — Submitted September 19, 2025*
> [https://doi.org/10.48550/arXiv.2509.15957](https://doi.org/10.48550/arXiv.2509.15957)

Their research validated that LLMs using custom MCP tools integrated with a hospital EHR database — tested with GPT-4.1 via a LangGraph ReAct agent — consistently selected and executed correct MCP tools with near-perfect accuracy across most clinical retrieval tasks. Their conclusion: EHR-MCP provides a foundation for hospital AI agents, with future work extending beyond retrieval to reasoning, generation, and clinical impact assessment.

This repository extends their concept with:
- A vendor-agnostic FHIR R4 abstraction layer (not tied to a single hospital system)
- SMART-on-FHIR Backend Services authentication
- Multi-agent framework compatibility (LangChain, CrewAI, LangGraph, AutoGen)
- Pre-packaged clinical context bundles for downstream agent consumption
- Open-source implementation for the broader healthcare AI ecosystem

---
*Part of a portfolio of healthcare agentic AI systems. See all projects at [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*
