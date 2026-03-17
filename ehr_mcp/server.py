"""
EHR-MCP Server

Defines all MCP tools exposed to agent frameworks.
Each tool maps to a FHIR operation or clinical context function.

Framework-agnostic: any MCP-compatible agent can call these tools.
Vendor-agnostic: routes to whichever FHIR R4 server is configured.

Available Tools:
  - get_patient_context     : Full clinical context bundle for a patient
  - get_patient             : Single Patient resource
  - get_conditions          : Active conditions for a patient
  - get_medications         : Active medication requests
  - get_observations        : Lab results and vitals
  - get_allergies           : Allergy/intolerance list
  - get_encounters          : Encounter history
  - get_diagnostic_reports  : Diagnostic report history
  - search_fhir             : Raw FHIR search (advanced use)
"""

import os
import logging
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from ehr_mcp.fhir_client import FHIRClient
from ehr_mcp.context_packager import ClinicalContextPackager
from ehr_mcp.schemas import (
    PatientContextRequest,
    ResourceSearchParams,
    FHIRResourceType,
    MCPToolResult,
)

logger = logging.getLogger(__name__)


def create_server() -> Server:
    server_name = os.getenv("MCP_SERVER_NAME", "ehr-mcp")
    server_version = os.getenv("MCP_SERVER_VERSION", "0.1.0")

    server = Server(server_name)
    fhir_client = FHIRClient()
    packager = ClinicalContextPackager(fhir_client)

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get_patient_context",
                description=(
                    "Retrieve a full clinical context bundle for a patient. "
                    "Returns patient demographics, conditions, medications, allergies, "
                    "observations, encounters, and diagnostic reports in a single call. "
                    "Use this as the primary tool for any clinical workflow agent."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string", "description": "FHIR Patient resource ID"},
                        "include_summary": {
                            "type": "boolean",
                            "description": "Include a plain-language clinical summary string",
                            "default": True,
                        },
                    },
                    "required": ["patient_id"],
                },
            ),
            types.Tool(
                name="get_patient",
                description="Retrieve a single Patient FHIR resource by ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string", "description": "FHIR Patient resource ID"},
                    },
                    "required": ["patient_id"],
                },
            ),
            types.Tool(
                name="get_conditions",
                description="Retrieve active conditions (diagnoses) for a patient.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "count": {"type": "integer", "default": 20, "description": "Max results"},
                    },
                    "required": ["patient_id"],
                },
            ),
            types.Tool(
                name="get_medications",
                description="Retrieve active medication requests for a patient.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "count": {"type": "integer", "default": 20},
                    },
                    "required": ["patient_id"],
                },
            ),
            types.Tool(
                name="get_observations",
                description="Retrieve observations (labs, vitals) for a patient.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "count": {"type": "integer", "default": 20},
                    },
                    "required": ["patient_id"],
                },
            ),
            types.Tool(
                name="get_allergies",
                description="Retrieve allergy and intolerance records for a patient.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "count": {"type": "integer", "default": 20},
                    },
                    "required": ["patient_id"],
                },
            ),
            types.Tool(
                name="get_encounters",
                description="Retrieve encounter history for a patient.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "count": {"type": "integer", "default": 10},
                    },
                    "required": ["patient_id"],
                },
            ),
            types.Tool(
                name="get_diagnostic_reports",
                description="Retrieve diagnostic reports for a patient.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "count": {"type": "integer", "default": 10},
                    },
                    "required": ["patient_id"],
                },
            ),
            types.Tool(
                name="search_fhir",
                description=(
                    "Raw FHIR R4 resource search. Use when specific resource types "
                    "or custom search parameters are needed beyond the standard tools."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "FHIR resource type (e.g. Patient, Observation, Condition)",
                        },
                        "patient_id": {"type": "string"},
                        "count": {"type": "integer", "default": 10},
                        "additional_params": {
                            "type": "object",
                            "description": "Additional FHIR search parameters as key-value pairs",
                        },
                    },
                    "required": ["resource_type"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        try:
            if name == "get_patient_context":
                request = PatientContextRequest(patient_id=arguments["patient_id"])
                bundle = await packager.build_context(request)
                include_summary = arguments.get("include_summary", True)

                result = bundle.model_dump()
                if include_summary:
                    result["_summary"] = packager.summarize(bundle)

                return [types.TextContent(type="text", text=str(result))]

            elif name == "get_patient":
                data = await fhir_client.get_patient(arguments["patient_id"])
                return [types.TextContent(type="text", text=str(data))]

            elif name == "get_conditions":
                data = await fhir_client.get_conditions(
                    arguments["patient_id"], arguments.get("count", 20)
                )
                return [types.TextContent(type="text", text=str(data))]

            elif name == "get_medications":
                data = await fhir_client.get_medications(
                    arguments["patient_id"], arguments.get("count", 20)
                )
                return [types.TextContent(type="text", text=str(data))]

            elif name == "get_observations":
                data = await fhir_client.get_observations(
                    arguments["patient_id"], arguments.get("count", 20)
                )
                return [types.TextContent(type="text", text=str(data))]

            elif name == "get_allergies":
                data = await fhir_client.get_allergies(
                    arguments["patient_id"], arguments.get("count", 20)
                )
                return [types.TextContent(type="text", text=str(data))]

            elif name == "get_encounters":
                data = await fhir_client.get_encounters(
                    arguments["patient_id"], arguments.get("count", 10)
                )
                return [types.TextContent(type="text", text=str(data))]

            elif name == "get_diagnostic_reports":
                data = await fhir_client.get_diagnostic_reports(
                    arguments["patient_id"], arguments.get("count", 10)
                )
                return [types.TextContent(type="text", text=str(data))]

            elif name == "search_fhir":
                params = ResourceSearchParams(
                    resource_type=FHIRResourceType(arguments["resource_type"]),
                    patient_id=arguments.get("patient_id"),
                    count=arguments.get("count", 10),
                    additional_params=arguments.get("additional_params"),
                )
                data = await fhir_client.search_resources(params)
                return [types.TextContent(type="text", text=str(data))]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            result = MCPToolResult(success=False, error=str(e))
            return [types.TextContent(type="text", text=str(result.model_dump()))]

    return server
