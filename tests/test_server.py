"""
Tests for ehr_mcp/server.py — MCP tool routing and error handling.

Verifies:
- All 9 tools are registered in list_tools()
- Tool routing dispatches to correct FHIRClient / Packager methods
- Error path returns MCPToolResult(success=False) — never raises to agent
- Unknown tool name returns graceful error string
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ehr_mcp.server import create_server
from ehr_mcp.schemas import ClinicalContextBundle


EXPECTED_TOOLS = {
    "get_patient_context",
    "get_patient",
    "get_conditions",
    "get_medications",
    "get_observations",
    "get_allergies",
    "get_encounters",
    "get_diagnostic_reports",
    "search_fhir",
}


@pytest.fixture
def mock_fhir_client():
    client = AsyncMock()
    client.get_patient = AsyncMock(return_value={"resourceType": "Patient", "id": "pt-001"})
    client.get_conditions = AsyncMock(return_value=[])
    client.get_medications = AsyncMock(return_value=[])
    client.get_observations = AsyncMock(return_value=[])
    client.get_allergies = AsyncMock(return_value=[])
    client.get_encounters = AsyncMock(return_value=[])
    client.get_diagnostic_reports = AsyncMock(return_value=[])
    client.search_resources = AsyncMock(return_value={"resourceType": "Bundle", "entry": []})
    return client


@pytest.fixture
def mock_packager(mock_fhir_client):
    packager = AsyncMock()
    packager.build_context = AsyncMock(
        return_value=ClinicalContextBundle(patient_id="pt-001")
    )
    packager.summarize = MagicMock(return_value="Patient pt-001: no active conditions.")
    return packager


class TestCreateServer:

    @pytest.mark.asyncio
    async def test_all_tools_registered(self, mock_fhir_client, mock_packager):
        with patch("ehr_mcp.server.FHIRClient", return_value=mock_fhir_client), \
             patch("ehr_mcp.server.ClinicalContextPackager", return_value=mock_packager):
            server = create_server()
            tools = await server.list_tools()
            tool_names = {t.name for t in tools}
            assert tool_names == EXPECTED_TOOLS

    @pytest.mark.asyncio
    async def test_get_patient_context_dispatches(self, mock_fhir_client, mock_packager):
        with patch("ehr_mcp.server.FHIRClient", return_value=mock_fhir_client), \
             patch("ehr_mcp.server.ClinicalContextPackager", return_value=mock_packager):
            server = create_server()
            result = await server.call_tool("get_patient_context", {"patient_id": "pt-001"})
            assert result
            assert len(result) == 1
            mock_packager.build_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_patient_dispatches(self, mock_fhir_client, mock_packager):
        with patch("ehr_mcp.server.FHIRClient", return_value=mock_fhir_client), \
             patch("ehr_mcp.server.ClinicalContextPackager", return_value=mock_packager):
            server = create_server()
            result = await server.call_tool("get_patient", {"patient_id": "pt-001"})
            mock_fhir_client.get_patient.assert_called_once_with("pt-001")
            assert result

    @pytest.mark.asyncio
    async def test_get_conditions_dispatches(self, mock_fhir_client, mock_packager):
        with patch("ehr_mcp.server.FHIRClient", return_value=mock_fhir_client), \
             patch("ehr_mcp.server.ClinicalContextPackager", return_value=mock_packager):
            server = create_server()
            await server.call_tool("get_conditions", {"patient_id": "pt-001"})
            mock_fhir_client.get_conditions.assert_called_once_with("pt-001", 20)

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error_string(self, mock_fhir_client, mock_packager):
        with patch("ehr_mcp.server.FHIRClient", return_value=mock_fhir_client), \
             patch("ehr_mcp.server.ClinicalContextPackager", return_value=mock_packager):
            server = create_server()
            result = await server.call_tool("nonexistent_tool", {})
            assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_exception_returns_mcp_error_result(self, mock_fhir_client, mock_packager):
        """Exceptions must never propagate to the agent — always return MCPToolResult error."""
        mock_fhir_client.get_patient = AsyncMock(side_effect=Exception("FHIR 503 timeout"))
        with patch("ehr_mcp.server.FHIRClient", return_value=mock_fhir_client), \
             patch("ehr_mcp.server.ClinicalContextPackager", return_value=mock_packager):
            server = create_server()
            result = await server.call_tool("get_patient", {"patient_id": "pt-001"})
            assert "FHIR 503 timeout" in result[0].text
            assert "False" in result[0].text  # MCPToolResult(success=False)
