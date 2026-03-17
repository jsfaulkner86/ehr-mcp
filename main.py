"""
EHR-MCP: Framework-Agnostic Interoperability Protocol
Entry point for the MCP server.

Vendor-agnostic — works with any FHIR R4 compliant EHR:
  Epic, Cerner, Oracle Health, Meditech, etc.

Auth: SMART-on-FHIR Backend Services (system-to-system)
"""

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from ehr_mcp.server import create_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting EHR-MCP Server...")
    server = create_server()
    asyncio.run(server.run_stdio())
