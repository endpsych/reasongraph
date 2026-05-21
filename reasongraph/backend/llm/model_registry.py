"""
LLM provider and model registry for ReasonGraph.

What this file does:
- Defines the initial provider/model options available to the app.
- Sets gpt-5-nano as the default OpenAI model for the MVP.
- Keeps model selection centralized instead of hardcoding model names in routes.
- Provides helpers for reading provider metadata and validating model choices.

How it fits into ReasonGraph:
- The frontend settings screen will read this registry.
- LLM workflows will later use this registry to validate provider/model choices.
- Provider routes and tests depend on these helpers.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from reasongraph.backend.schemas.provider import (
    ProviderInfo,
    ProviderModelInfo,
    ProviderName,
    ProviderRegistryRead,
)

# ---------------------------------------------------------------------
# Registry data
# ---------------------------------------------------------------------

OPENAI_MODELS = [
    ProviderModelInfo(
        id="gpt-5-nano",
        display_name="GPT-5 Nano",
        description=(
            "Default ReasonGraph MVP model. Fast, low-cost OpenAI model "
            "suitable for early extraction and classification workflows."
        ),
    ),
    ProviderModelInfo(
        id="gpt-5.4-nano",
        display_name="GPT-5.4 Nano",
        description=(
            "Newer nano model option for speed- and cost-sensitive workloads."
        ),
    ),
    ProviderModelInfo(
        id="gpt-5.4-mini",
        display_name="GPT-5.4 Mini",
        description="Stronger low-latency model option for higher-quality reasoning tasks.",
    ),
    ProviderModelInfo(
        id="gpt-5.5",
        display_name="GPT-5.5",
        description="Higher-capability OpenAI model for complex reasoning and coding tasks.",
    ),
]

PROVIDERS = [
    ProviderInfo(
        id=ProviderName.openai,
        display_name="OpenAI",
        env_var="OPENAI_API_KEY",
        default_model="gpt-5-nano",
        models=OPENAI_MODELS,
    )
]


# ---------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------


def get_provider_registry() -> ProviderRegistryRead:
    """Return the public provider registry."""
    return ProviderRegistryRead(providers=PROVIDERS)


def get_provider_info(provider: ProviderName) -> ProviderInfo | None:
    """Return provider information by provider ID."""
    for provider_info in PROVIDERS:
        if provider_info.id == provider:
            return provider_info

    return None


def is_supported_model(provider: ProviderName, model: str) -> bool:
    """Return whether a model is listed for a provider."""
    provider_info = get_provider_info(provider)

    if provider_info is None:
        return False

    return any(model_info.id == model for model_info in provider_info.models)