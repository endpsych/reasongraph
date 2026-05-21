"""
Provider settings schemas for ReasonGraph.

What this file does:
- Defines API request and response models for LLM provider settings.
- Supports provider/model selection.
- Supports API key storage modes such as session-only, local key vault, and environment.
- Ensures API responses never expose raw API keys.

How it fits into ReasonGraph:
- The frontend will use these schemas to let users configure OpenAI or other providers.
- Provider settings are needed before ReasonGraph can run extraction and LLM POV workflows.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from enum import StrEnum

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------


class ProviderName(StrEnum):
    """Supported LLM providers."""

    openai = "openai"


class KeyStorageMode(StrEnum):
    """Supported API key storage modes."""

    session_only = "session_only"
    local_key_vault = "local_key_vault"
    environment = "environment"


# ---------------------------------------------------------------------
# Provider registry schemas
# ---------------------------------------------------------------------


class ProviderModelInfo(BaseModel):
    """Public information about one available model."""

    id: str
    display_name: str
    description: str = ""


class ProviderInfo(BaseModel):
    """Public information about one available provider."""

    id: ProviderName
    display_name: str
    env_var: str
    default_model: str
    models: list[ProviderModelInfo]


class ProviderRegistryRead(BaseModel):
    """Public registry of available LLM providers."""

    providers: list[ProviderInfo]


# ---------------------------------------------------------------------
# Provider profile schemas
# ---------------------------------------------------------------------


class ProviderProfileUpsert(BaseModel):
    """Request to create or update provider settings."""

    provider: ProviderName = ProviderName.openai
    profile_name: str = "default"
    selected_model: str
    key_storage_mode: KeyStorageMode = KeyStorageMode.session_only
    api_key: str | None = Field(
        default=None,
        description="Raw API key. Used only for session or key-vault storage. Never returned.",
    )


class ProviderProfileRead(BaseModel):
    """Safe provider profile response that never exposes the raw API key."""

    id: str
    provider: str
    profile_name: str
    selected_model: str
    key_storage_mode: str
    keyring_service_name: str
    keyring_username: str
    has_saved_key: bool


class ProviderConnectionTestRequest(BaseModel):
    """Request to test whether a provider/model configuration is usable."""

    provider: ProviderName = ProviderName.openai
    model: str
    profile_name: str = "default"
    key_storage_mode: KeyStorageMode = KeyStorageMode.session_only
    api_key: str | None = None


class ProviderConnectionTestRead(BaseModel):
    """Response from a provider connection test."""

    provider: str
    model: str
    ok: bool
    message: str