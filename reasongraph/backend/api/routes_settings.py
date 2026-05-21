"""
Settings API routes for ReasonGraph.

What this file does:
- Exposes provider/model registry endpoints.
- Lets users save provider profile metadata.
- Supports local key vault API key storage.
- Supports deleting saved provider keys.
- Supports testing provider/model connectivity.

How it fits into ReasonGraph:
- These routes power the future frontend settings screen.
- They prepare ReasonGraph for OpenAI-powered extraction and LLM POV workflows.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException

from reasongraph.backend.db.session import get_session
from reasongraph.backend.llm.model_registry import get_provider_registry
from reasongraph.backend.schemas.provider import (
    ProviderConnectionTestRead,
    ProviderConnectionTestRequest,
    ProviderName,
    ProviderProfileRead,
    ProviderProfileUpsert,
    ProviderRegistryRead,
)
from reasongraph.backend.services.provider_service import (
    delete_provider_profile_key,
    list_provider_profiles,
    test_provider_connection,
    upsert_provider_profile,
)

# ---------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------

router = APIRouter(prefix="/settings", tags=["settings"])


# ---------------------------------------------------------------------
# Provider registry routes
# ---------------------------------------------------------------------


@router.get("/providers", response_model=ProviderRegistryRead)
def get_providers_route() -> ProviderRegistryRead:
    """Return available providers and models."""
    return get_provider_registry()


# ---------------------------------------------------------------------
# Provider profile routes
# ---------------------------------------------------------------------


@router.get("/provider-profiles", response_model=list[ProviderProfileRead])
def list_provider_profiles_route() -> list[ProviderProfileRead]:
    """List saved provider profile metadata without exposing raw keys."""
    with get_session() as session:
        return list_provider_profiles(session)


@router.post("/provider-profiles", response_model=ProviderProfileRead)
def upsert_provider_profile_route(
    profile_in: ProviderProfileUpsert,
) -> ProviderProfileRead:
    """Create or update a provider profile."""
    with get_session() as session:
        try:
            return upsert_provider_profile(session=session, profile_in=profile_in)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error


@router.delete("/provider-profiles/{provider}/{profile_name}/key")
def delete_provider_profile_key_route(
    provider: ProviderName,
    profile_name: str,
) -> dict[str, bool]:
    """Delete one saved provider API key from the local key vault."""
    with get_session() as session:
        deleted = delete_provider_profile_key(
            session=session,
            provider=provider,
            profile_name=profile_name,
        )

    return {"deleted": deleted}


# ---------------------------------------------------------------------
# Provider connection test route
# ---------------------------------------------------------------------


@router.post("/providers/test", response_model=ProviderConnectionTestRead)
def test_provider_connection_route(
    request: ProviderConnectionTestRequest,
) -> ProviderConnectionTestRead:
    """Test provider/model connectivity."""
    return test_provider_connection(request)