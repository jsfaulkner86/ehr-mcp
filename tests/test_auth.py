"""
Tests for ehr_mcp/auth.py — SMART-on-FHIR Backend Services auth.

All HTTP calls and filesystem I/O are mocked.
No live EHR credentials or network access required.
"""

import time
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from ehr_mcp.auth import SMARTBackendAuth


MOCK_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA2a2rwplBQLzHPZe5TNJF9bHBEbHVr6JswOlhFBGM5uZL
-----END RSA PRIVATE KEY-----"""


class TestSMARTBackendAuth:

    def _make_auth(self, key_exists=True):
        with patch.object(Path, "exists", return_value=key_exists), \
             patch.object(Path, "read_text", return_value=MOCK_PRIVATE_KEY):
            auth = SMARTBackendAuth(
                token_url="https://fhir.epic.com/oauth2/token",
                client_id="test-client-id",
                private_key_path="./keys/private_key.pem",
            )
        return auth

    def test_init_loads_private_key(self):
        auth = self._make_auth(key_exists=True)
        assert auth._private_key == MOCK_PRIVATE_KEY

    def test_init_missing_key_does_not_raise(self):
        """Missing key logs warning but does not crash — server still starts."""
        with patch.object(Path, "exists", return_value=False):
            auth = SMARTBackendAuth(
                token_url="https://fhir.epic.com/oauth2/token",
                client_id="test-client-id",
                private_key_path="./keys/private_key.pem",
            )
        assert auth._private_key is None

    def test_token_url_from_env(self, monkeypatch):
        monkeypatch.setenv("SMART_TOKEN_URL", "https://env-token-url.example.com/token")
        monkeypatch.setenv("SMART_CLIENT_ID", "env-client-id")
        with patch.object(Path, "exists", return_value=False):
            auth = SMARTBackendAuth()
        assert auth.token_url == "https://env-token-url.example.com/token"
        assert auth.client_id == "env-client-id"

    @pytest.mark.asyncio
    async def test_get_token_returns_cached_token(self):
        """Token is cached and not re-fetched if still valid."""
        auth = self._make_auth()
        auth._token = "cached-token-xyz"
        auth._token_expires_at = time.time() + 3600  # valid for 1 hour
        token = await auth.get_token()
        assert token == "cached-token-xyz"

    @pytest.mark.asyncio
    async def test_get_token_refreshes_expired_token(self):
        """Expired token triggers a new token request."""
        auth = self._make_auth()
        auth._token = "old-token"
        auth._token_expires_at = time.time() - 100  # already expired

        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "new-token-abc", "expires_in": 3600}
        mock_response.raise_for_status = MagicMock()

        with patch("ehr_mcp.auth.jwt.encode", return_value="mock.jwt.assertion"), \
             patch("ehr_mcp.auth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            token = await auth.get_token()

        assert token == "new-token-abc"
        assert auth._token == "new-token-abc"

    @pytest.mark.asyncio
    async def test_get_token_sets_expiry(self):
        """Token expiry is set correctly from expires_in."""
        auth = self._make_auth()
        auth._token = None
        auth._token_expires_at = 0

        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "fresh-token", "expires_in": 1800}
        mock_response.raise_for_status = MagicMock()

        before = time.time()
        with patch("ehr_mcp.auth.jwt.encode", return_value="mock.jwt.assertion"), \
             patch("ehr_mcp.auth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client
            await auth.get_token()

        assert auth._token_expires_at >= before + 1800 - 5  # 5s tolerance
