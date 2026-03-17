"""
LangChain Integration Example

Demonstrates how to connect a LangChain agent to EHR-MCP.
The agent can call any EHR-MCP tool using natural language.

Prerequisites:
  - EHR-MCP server running (python main.py)
  - .env configured with FHIR_BASE_URL and SMART credentials
  - pip install langchain langchain-openai mcp
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools


SYSTEM_PROMPT = """You are a clinical workflow assistant with access to a patient's EHR data 
via FHIR R4. You can retrieve patient context, conditions, medications, observations, 
allergies, encounters, and diagnostic reports.

Always retrieve patient context before making clinical recommendations.
Never fabricate clinical data — only use what is returned from EHR tools."""


async def run_clinical_agent(patient_id: str, query: str):
    server_params = StdioServerParameters(
        command="python",
        args=["main.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])

            agent = create_tool_calling_agent(llm, tools, prompt)
            executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

            result = await executor.ainvoke({
                "input": f"Patient ID: {patient_id}. {query}"
            })
            return result["output"]


if __name__ == "__main__":
    patient_id = "example-patient-123"
    query = "Retrieve this patient's full clinical context and summarize their active conditions and medications."
    result = asyncio.run(run_clinical_agent(patient_id, query))
    print(result)
