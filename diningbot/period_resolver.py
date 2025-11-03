"""Helpers for resolving daily DiningBot period identifiers."""

from __future__ import annotations

import logging
from typing import Dict

from diningbot import api as dine_api

DEFAULT_LOCATION_ID = "63fd054f92d6b41e84b6c30e"
PERIOD_KEYS = ("breakfast", "lunch", "dinner")

_logger = logging.getLogger(__name__)


def _normalize_period_name(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


def resolve_period_ids(date: str) -> Dict[str, str]:
    """Resolve dynamic period IDs by matching names from the daily menu."""

    matches: Dict[str, str] = {}
    try:
        menu_data = dine_api.fetch_menu(DEFAULT_LOCATION_ID, date=date, platform=0)
    except dine_api.ApiError as exc:
        _logger.error("Failed to fetch menu for %s: %s", date, exc)
        raise RuntimeError("Unable to fetch menu data for period resolution") from exc

    if isinstance(menu_data, dict):
        # raw periods list often contains the daily ids even when categories are empty
        raw_periods = menu_data.get("periods")
        if isinstance(raw_periods, list):
            for item in raw_periods:
                if not isinstance(item, dict):
                    continue
                pid = item.get("id")
                name = item.get("name")
                if pid and name:
                    matches[_normalize_period_name(str(name))] = str(pid)
        # fallback to parsed menu (may only include currently active period)
        if not matches:
            try:
                parsed_menu = dine_api.parse_menu(menu_data)
            except Exception as exc:  # pragma: no cover - defensive parsing path
                _logger.error("Failed to parse menu data for %s: %s", date, exc)
                parsed_menu = None
            if parsed_menu:
                for period in parsed_menu.periods:
                    if not period.id or not period.name:
                        continue
                    matches[_normalize_period_name(period.name)] = period.id

    resolved: Dict[str, str] = {}
    missing: list[str] = []
    for key in PERIOD_KEYS:
        norm = _normalize_period_name(key)
        pid = matches.get(norm)
        if pid is None:
            pid = next((pid for name_norm, pid in matches.items() if norm in name_norm), None)
        if pid:
            resolved[key] = pid
        else:
            missing.append(key)

    if missing:
        _logger.error(
            "Menu data for %s missing period ids for: %s (matched ids: %s)",
            date,
            ", ".join(missing),
            resolved or "none",
        )
        raise RuntimeError(f"Missing period ids: {', '.join(missing)}")

    return resolved
