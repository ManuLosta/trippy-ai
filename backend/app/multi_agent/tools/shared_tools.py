"""Shared tools for the multi-agent system.

These tools are imported from the legacy agent to maintain consistency.
"""

import sys
from pathlib import Path

# Add parent directory to path to import from legacy_agent
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.legacy_agent.main import (
    search_flights,
    search_activities,
    get_weather,
    convert_usd_to_ars,
)

__all__ = [
    "search_flights",
    "search_activities",
    "get_weather",
    "convert_usd_to_ars",
]
