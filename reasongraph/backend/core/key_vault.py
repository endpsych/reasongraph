"""
Local API key vault utilities for ReasonGraph.

What this file does:
- Provides a small wrapper around Python keyring.
- Saves API keys into the local operating-system key vault when available.
- Retrieves saved API keys without exposing them through API responses.
- Deletes individual keys or all ReasonGraph-managed provider keys.

How it fits into ReasonGraph:
- ReasonGraph users need to provide LLM provider API keys.
- Session-only keys are safest for MVP use.
- Local key vault storage improves UX while avoiding plaintext SQLite storage.

Security notes:
- Raw API keys must never be logged.
- Raw API keys must never be returned from API routes.
- SQLite stores only key metadata, not the raw key.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import keyring

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

DEFAULT_KEYRING_SERVICE_NAME = "reasongraph"


# ---------------------------------------------------------------------
# Key identity helpers
# ---------------------------------------------------------------------


def build_keyring_username(provider: str, profile_name: str) -> str:
    """Build a stable keyring username for a provider profile."""
    return f"{provider}:{profile_name}"


# ---------------------------------------------------------------------
# Key vault operations
# ---------------------------------------------------------------------


def save_api_key(
    provider: str,
    profile_name: str,
    api_key: str,
    service_name: str = DEFAULT_KEYRING_SERVICE_NAME,
) -> str:
    """
    Save an API key in the local OS key vault.

    Returns:
        The keyring username used to store the key.
    """
    username = build_keyring_username(provider=provider, profile_name=profile_name)
    keyring.set_password(service_name, username, api_key)
    return username


def get_api_key(
    provider: str,
    profile_name: str,
    service_name: str = DEFAULT_KEYRING_SERVICE_NAME,
) -> str | None:
    """Retrieve an API key from the local OS key vault."""
    username = build_keyring_username(provider=provider, profile_name=profile_name)
    return keyring.get_password(service_name, username)


def delete_api_key(
    provider: str,
    profile_name: str,
    service_name: str = DEFAULT_KEYRING_SERVICE_NAME,
) -> bool:
    """
    Delete one API key from the local OS key vault.

    Returns:
        True if deletion succeeded or the key did not exist.
        False if the keyring backend raised an unexpected error.
    """
    username = build_keyring_username(provider=provider, profile_name=profile_name)

    try:
        keyring.delete_password(service_name, username)
    except keyring.errors.PasswordDeleteError:
        return True
    except keyring.errors.InitError:
        return False

    return True