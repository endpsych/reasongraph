"""
Provider settings service for ReasonGraph.

What this file does:
- Creates and updates provider profile metadata in SQLite.
- Saves API keys to the local key vault when requested.
- Resolves API keys from session input, local key vault, or environment variables.
- Tests OpenAI provider connectivity without exposing secrets.

How it fits into ReasonGraph:
- Provider settings are required before extraction and LLM POV workflows can call LLMs.
- SQLite stores only safe provider metadata.
- Raw API keys are handled in memory or through keyring, never plaintext SQLite.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import os

from openai import OpenAI
from sqlmodel import Session, select

from reasongraph.backend.core.key_vault import (
    DEFAULT_KEYRING_SERVICE_NAME,
    build_keyring_username,
    delete_api_key,
    get_api_key,
    save_api_key,
)
from reasongraph.backend.db.models import ProviderProfile
from reasongraph.backend.llm.model_registry import get_provider_info, is_supported_model
from reasongraph.backend.schemas.provider import (
    KeyStorageMode,
    ProviderConnectionTestRead,
    ProviderConnectionTestRequest,
    ProviderName,
    ProviderProfileRead,
    ProviderProfileUpsert,
)

# ---------------------------------------------------------------------
# Provider profile helpers
# ---------------------------------------------------------------------


def _get_provider_profile(
    session: Session,
    provider: str,
    profile_name: str,
) -> ProviderProfile | None:
    """Return an existing provider profile from SQLite."""
    statement = (
        select(ProviderProfile)
        .where(ProviderProfile.provider == provider)
        .where(ProviderProfile.profile_name == profile_name)
    )
    return session.exec(statement).first()


def _profile_to_read(profile: ProviderProfile, has_saved_key: bool) -> ProviderProfileRead:
    """Convert a ProviderProfile model into a safe API response."""
    return ProviderProfileRead(
        id=profile.id,
        provider=profile.provider,
        profile_name=profile.profile_name,
        selected_model=profile.selected_model,
        key_storage_mode=profile.key_storage_mode,
        keyring_service_name=profile.keyring_service_name,
        keyring_username=profile.keyring_username,
        has_saved_key=has_saved_key,
    )


def upsert_provider_profile(
    session: Session,
    profile_in: ProviderProfileUpsert,
) -> ProviderProfileRead:
    """
    Create or update provider profile metadata.

    Raw API keys are only saved if key_storage_mode is local_key_vault.
    """
    if not is_supported_model(profile_in.provider, profile_in.selected_model):
        raise ValueError(
            f"Unsupported model '{profile_in.selected_model}' for provider "
            f"'{profile_in.provider}'."
        )

    provider = str(profile_in.provider)
    profile_name = profile_in.profile_name

    profile = _get_provider_profile(
        session=session,
        provider=provider,
        profile_name=profile_name,
    )

    keyring_service_name = DEFAULT_KEYRING_SERVICE_NAME
    keyring_username = build_keyring_username(
        provider=provider,
        profile_name=profile_name,
    )

    if profile is None:
        profile = ProviderProfile(
            provider=provider,
            profile_name=profile_name,
            selected_model=profile_in.selected_model,
            key_storage_mode=str(profile_in.key_storage_mode),
            keyring_service_name=keyring_service_name,
            keyring_username=keyring_username,
        )
    else:
        profile.selected_model = profile_in.selected_model
        profile.key_storage_mode = str(profile_in.key_storage_mode)
        profile.keyring_service_name = keyring_service_name
        profile.keyring_username = keyring_username

    has_saved_key = False

    if profile_in.key_storage_mode == KeyStorageMode.local_key_vault:
        if not profile_in.api_key:
            existing_key = get_api_key(provider=provider, profile_name=profile_name)
            has_saved_key = existing_key is not None
        else:
            save_api_key(
                provider=provider,
                profile_name=profile_name,
                api_key=profile_in.api_key,
            )
            has_saved_key = True

    session.add(profile)
    session.commit()
    session.refresh(profile)

    if profile_in.key_storage_mode == KeyStorageMode.local_key_vault:
        has_saved_key = get_api_key(provider=provider, profile_name=profile_name) is not None

    return _profile_to_read(profile=profile, has_saved_key=has_saved_key)


def list_provider_profiles(session: Session) -> list[ProviderProfileRead]:
    """List all saved provider profile metadata without exposing raw keys."""
    statement = select(ProviderProfile).order_by(ProviderProfile.provider.asc())
    profiles = list(session.exec(statement).all())

    result = []

    for profile in profiles:
        has_saved_key = False

        if profile.key_storage_mode == KeyStorageMode.local_key_vault:
            has_saved_key = (
                get_api_key(
                    provider=profile.provider,
                    profile_name=profile.profile_name,
                    service_name=profile.keyring_service_name,
                )
                is not None
            )

        result.append(_profile_to_read(profile=profile, has_saved_key=has_saved_key))

    return result


def delete_provider_profile_key(
    session: Session,
    provider: ProviderName,
    profile_name: str,
) -> bool:
    """Delete one saved provider key from the local key vault."""
    profile = _get_provider_profile(
        session=session,
        provider=str(provider),
        profile_name=profile_name,
    )

    service_name = (
        profile.keyring_service_name
        if profile is not None
        else DEFAULT_KEYRING_SERVICE_NAME
    )

    return delete_api_key(
        provider=str(provider),
        profile_name=profile_name,
        service_name=service_name,
    )


# ---------------------------------------------------------------------
# API key resolution
# ---------------------------------------------------------------------


def resolve_api_key(request: ProviderConnectionTestRequest) -> str | None:
    """
    Resolve an API key according to the selected storage mode.

    Resolution order:
    - session_only: use key provided in the request
    - local_key_vault: load from keyring, or use request key as fallback
    - environment: load from provider environment variable
    """
    provider_info = get_provider_info(request.provider)

    if provider_info is None:
        return None

    if request.key_storage_mode == KeyStorageMode.session_only:
        return request.api_key

    if request.key_storage_mode == KeyStorageMode.local_key_vault:
        saved_key = get_api_key(
            provider=str(request.provider),
            profile_name=request.profile_name,
        )
        return saved_key or request.api_key

    if request.key_storage_mode == KeyStorageMode.environment:
        return os.getenv(provider_info.env_var)

    return None


# ---------------------------------------------------------------------
# Provider connection tests
# ---------------------------------------------------------------------


def test_provider_connection(
    request: ProviderConnectionTestRequest,
) -> ProviderConnectionTestRead:
    """
    Test whether a provider/model configuration can be used.

    This uses a minimal OpenAI models retrieval call for the MVP.
    """
    if request.provider != ProviderName.openai:
        return ProviderConnectionTestRead(
            provider=str(request.provider),
            model=request.model,
            ok=False,
            message="Only OpenAI is supported in the MVP.",
        )

    if not is_supported_model(request.provider, request.model):
        return ProviderConnectionTestRead(
            provider=str(request.provider),
            model=request.model,
            ok=False,
            message=f"Unsupported model: {request.model}",
        )

    api_key = resolve_api_key(request)

    if not api_key:
        return ProviderConnectionTestRead(
            provider=str(request.provider),
            model=request.model,
            ok=False,
            message="No API key available for the selected storage mode.",
        )

    try:
        client = OpenAI(api_key=api_key)
        client.models.retrieve(request.model)
    except Exception as error:
        return ProviderConnectionTestRead(
            provider=str(request.provider),
            model=request.model,
            ok=False,
            message=f"Connection test failed: {error}",
        )

    return ProviderConnectionTestRead(
        provider=str(request.provider),
        model=request.model,
        ok=True,
        message="Connection test succeeded.",
    )