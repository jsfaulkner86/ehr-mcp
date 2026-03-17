"""
CrewAI Integration Example

Demonstrates a multi-agent crew that uses EHR-MCP tools
to perform a prior authorization workflow:

  Agent 1 (Clinical Reviewer): Retrieves patient context from EHR
  Agent 2 (Prior Auth Analyst): Evaluates clinical criteria
  Agent 3 (Documentation Specialist): Drafts the prior auth submission

Prerequisites:
  - EHR-MCP server running (python main.py)
  - .env configured with FHIR_BASE_URL and SMART credentials
  - pip install crewai mcp
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPTool


def build_prior_auth_crew(patient_id: str, requested_service: str) -> Crew:
    ehr_tool = MCPTool(server_script_path="main.py")

    clinical_reviewer = Agent(
        role="Clinical Reviewer",
        goal="Retrieve and interpret the patient's complete clinical history from the EHR.",
        backstory=(
            "You are a senior clinician with deep experience reading FHIR-based EHR data. "
            "You know exactly which clinical facts matter for prior authorization decisions."
        ),
        tools=[ehr_tool],
        verbose=True,
    )

    prior_auth_analyst = Agent(
        role="Prior Authorization Analyst",
        goal="Evaluate whether the requested service meets clinical necessity criteria.",
        backstory=(
            "You are an expert in payer clinical criteria, medical necessity guidelines, "
            "and prior authorization requirements across commercial and government payers."
        ),
        verbose=True,
    )

    documentation_specialist = Agent(
        role="Documentation Specialist",
        goal="Draft a complete, submission-ready prior authorization request.",
        backstory=(
            "You produce clear, evidence-backed prior auth documentation "
            "that reduces payer denials and speeds up approvals."
        ),
        verbose=True,
    )

    retrieve_context = Task(
        description=f"Retrieve the full clinical context for patient ID {patient_id}. "
                    f"Focus on conditions, medications, and recent observations relevant to: {requested_service}",
        expected_output="Structured clinical summary with relevant history for the requested service.",
        agent=clinical_reviewer,
    )

    evaluate_criteria = Task(
        description=f"Using the clinical summary, evaluate whether {requested_service} meets "
                    f"medical necessity criteria. Identify supporting and conflicting evidence.",
        expected_output="Clinical necessity assessment with supporting evidence cited from EHR data.",
        agent=prior_auth_analyst,
    )

    draft_submission = Task(
        description="Draft a complete prior authorization submission document based on the clinical "
                    "necessity assessment. Include patient demographics, clinical justification, "
                    "supporting diagnoses, and requested service details.",
        expected_output="Submission-ready prior authorization document.",
        agent=documentation_specialist,
    )

    return Crew(
        agents=[clinical_reviewer, prior_auth_analyst, documentation_specialist],
        tasks=[retrieve_context, evaluate_criteria, draft_submission],
        process=Process.sequential,
        verbose=True,
    )


if __name__ == "__main__":
    patient_id = "example-patient-123"
    requested_service = "MRI lumbar spine without contrast"

    crew = build_prior_auth_crew(patient_id, requested_service)
    result = crew.kickoff()
    print(result)
