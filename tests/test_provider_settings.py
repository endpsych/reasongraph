"""
Tests for ReasonGraph provider settings helpers.

What this file does:
- Tests the provider registry.
- Tests model support checks.
- Tests keyring username construction.
- Avoids testing real provider connections or storing real API keys.

How it fits into ReasonGraph:
- Provider settings are security-sensitive because they involve API key handling.
- These tests protect non-secret logic without requiring network access.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from reasongraph.backend.core.key_vault import build_keyring_username
from reasongraph.backend.llm.model_registry import (
    get_provider_info,
    get_provider_registry,
    is_supported_model,
)
from reasongraph.backend.schemas.provider import ProviderName

# ---------------------------------------------------------------------
# Provider registry tests
# ---------------------------------------------------------------------


def test_provider_registry_contains_openai() -> None:
    """Provider registry should expose OpenAI for the MVP."""
    registry = get_provider_registry()

    assert len(registry.providers) >= 1
    assert registry.providers[0].id == ProviderName.openai


def test_get_provider_info_openai() -> None:
    """OpenAI provider info should include an environment variable and models."""
    provider_info = get_provider_info(ProviderName.openai)

    assert provider_info is not None
    assert provider_info.display_name == "OpenAI"
    assert provider_info.env_var == "OPENAI_API_KEY"
    assert len(provider_info.models) >= 1


def test_supported_model_check() -> None:
    """Known OpenAI models should be supported."""
    assert is_supported_model(ProviderName.openai, "gpt-5-nano") is True


def test_unsupported_model_check() -> None:
    """Unknown models should not be supported."""
    assert is_supported_model(ProviderName.openai, "not-a-real-model") is False


# ---------------------------------------------------------------------
# Key vault identity tests
# ---------------------------------------------------------------------


def test_build_keyring_username() -> None:
    """Keyring username should be stable and provider-specific."""
    username = build_keyring_username(provider="openai", profile_name="default")

    assert username == "openai:default"