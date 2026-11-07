"""Shared pytest fixtures."""

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def anyio_backend() -> str:
    """Run async tests on asyncio only.

    Returns:
        The anyio backend name.
    """
    return "asyncio"


@pytest.fixture
def marine_payload() -> dict[str, Any]:
    """Load the saved Open-Meteo Marine response.

    Returns:
        The decoded JSON payload.
    """
    payload: dict[str, Any] = json.loads(
        (FIXTURES / "open_meteo_marine.json").read_text()
    )
    return payload
