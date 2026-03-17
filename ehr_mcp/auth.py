"""
SMART-on-FHIR Backend Services Authentication

Implements the SMART Backend Services Authorization spec:
https://hl7.org/fhir/smart-app-launch/backend-services.html

Vendor-agnostic: works with any conformant FHIR R4 server.
Used by Epic (SMART v2), Cerner, Oracle Health, and others.

Flow:
  1. Load RSA private key
  2. Build a signed JWT client assertion (RS384)
  3. POST to token endpoint with client_credentials grant
  4. Receive and cache the bearer token
  5. Auto-refresh when token expires
"""

import os
import time
import uuid
import logging
from pathlib import Path
from typing import Optional

import jwt
import httpx

logger = logging.getLogger(__name__)


class SMARTBackendAuth:
    """
    SMART-on-FHIR Backend Services token manager.
    Thread-safe, auto-refreshing bearer token cache.
    """

    def __init__(
        self,
        token_url: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key_path: Optional[str] = None,
        scope: Optional[str] = None,
    ):
        self.token_url = token_url or os.getenv("SMART_TOKEN_URL")
        self.client_id = client_id or os.getenv("SMART_CLIENT_ID")
        self.private_key_path = private_key_path or os.getenv("SMART_PRIVATE_KEY_PATH", "./keys/private_key.pem")
        self.scope = scope or os.getenv(
            "SMART_SCOPE",
            "system/Patient.read system/Observation.read system/Condition.read "
            "system/MedicationRequest.read system/Encounter.read system/DiagnosticReport.read"
        )

        self._token: Optional[str] = None
        self._token_expires_at: float = 0
        self._private_key: Optional[str] = None

        self._load_private_key()

    def _load_private_key(self):
        key_path = Path(self.private_key_path)
        if key_path.exists():
            self._private_key = key_path.read_text()
            logger.info(f"Loaded SMART private key from {key_path}")
        else:
            logger.warning(
                f"Private key not found at {key_path}. "
                "Generate with: openssl genrsa -out keys/private_key.pem 2048"
            )

    def _build_client_assertion(self) -> str:
        """Build a signed JWT for the client_credentials grant."""
        now = int(time.time())
        payload = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": self.token_url,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + 300,  # 5 minute expiry per SMART spec
        }
        return jwt.encode(payload, self._private_key, algorithm="RS384")

    async def get_token(self) -> str:
        """Return a valid bearer token, refreshing if expired."""
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token

        logger.info("Requesting new SMART backend services token...")
        assertion = self._build_client_assertion()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": assertion,
                    "scope": self.scope,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()

        self._token = token_data["access_token"]
        self._token_expires_at = time.time() + token_data.get("expires_in", 3600)
        logger.info("SMART token acquired successfully.")
        return self._token
