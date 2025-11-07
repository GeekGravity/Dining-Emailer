"""Shared helpers that orchestrate DiningBot's data fetch and email send."""

from __future__ import annotations

import logging

from concurrent.futures import ThreadPoolExecutor, as_completed
from diningbot import fetch_helper as dine_api

DEFAULT_LOCATION_ID = "63fd054f92d6b41e84b6c30e"
PERIOD_KEYS = ("breakfast", "lunch", "dinner")

_logger = logging.getLogger(__name__)

def fetch_daily_menu(date: str) -> dict[str, dine_api.Period]:  # type: ignore[attr-defined]
    """Fetch and parse each dining period for the given date."""

    period_ids = dine_api.resolve_period_ids(date)
     
    if not period_ids:
        raise RuntimeError("No period ids resolved")

    parsed_periods: dict[str, dine_api.Period] = {}  # type: ignore[attr-defined]

    def _fetch(key: str, period_id: str) -> tuple[str, dict]:
        data = dine_api.fetch_period(DEFAULT_LOCATION_ID, period_id, date=date, platform=0)
        return key, data

    with ThreadPoolExecutor(max_workers=len(period_ids)) as executor:
        futures = {executor.submit(_fetch, key, pid): key for key, pid in period_ids.items()}
        for future in as_completed(futures):
            key = futures[future]
            try:
                _, data = future.result()
            except dine_api.ApiError as exc:  # type: ignore[attr-defined]
                raise RuntimeError(f"API error retrieving {key}: {exc}") from exc
            parsed_periods[key] = dine_api.parse_period(data)

    ordered_periods: dict[str, dine_api.Period] = {}  # type: ignore[attr-defined]
    for key in PERIOD_KEYS:
        if key in parsed_periods:
            ordered_periods[key] = parsed_periods[key]

    return ordered_periods