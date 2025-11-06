"""Shared helpers that orchestrate DiningBot's data fetch and email send."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from diningbot.helpers.repeats import (
    norm,
    RISE_AND_DINE,
    STACKS,
    LEAF_MARKET,
    GRILL_HOUSE,
    TEPPAN_SIGNATURE,
    FRENCH_TOAST_SIGNATURE,
    PANCAKE_SIGNATURE,
    RICE_BOWL_SIGNATURE,
    MEZZE_BAR_SIGNATURE,
    RAMEN_BAR_SIGNATURE,
    CURRY_BAR_SIGNATURE,
    PASTA_BAR_SIGNATURE,
)
from diningbot.helpers import api as dine_api
from diningbot.helpers import emailer
from diningbot.helpers.period_resolver import DEFAULT_LOCATION_ID, PERIOD_KEYS, resolve_period_ids
from typing import Dict


def fetch_daily_periods(date: str) -> dict[str, dine_api.Period]:  # type: ignore[attr-defined]
    """Fetch and parse each dining period for the given date."""

    period_ids = resolve_period_ids(date)
     
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


def build_plain_text(subject: str, periods: dict[str, dine_api.Period]) -> str:  # type: ignore[attr-defined]
    """Generate a plaintext companion for the email."""

    lines = [subject, ""]
    for key in PERIOD_KEYS:
        period = periods.get(key)
        if not period:
            continue
        lines.append(period.name or key.title())
        for category in period.categories:
            if not category.items:
                continue
            item_names = ", ".join(item.name for item in category.items if item.name)
            if item_names:
                label = category.name or "Misc"
                lines.append(f"  {label}: {item_names}")
        lines.append("")
    return "\n".join(lines).strip()


def send_menu_email(date: str, html_output: str, periods: dict[str, dine_api.Period]) -> None:  # type: ignore[attr-defined]
    """Load email settings and dispatch the menu email."""

    try:
        settings = emailer.load_email_settings()
    except ValueError as exc:
        raise RuntimeError(f"Invalid email settings: {exc}") from exc

    subject = f"Dining Menu - {date}"
    plain_text = build_plain_text(subject, periods)
    emailer.send_email(settings, subject, html_output, plain_text)

def _handle_type1_unique(cat: dine_api.Category) -> dine_api.Category:
    """
    TYPE1: Always unique stations.
    Just return as-is.
    """
    return cat

def _handle_type2_hybrid(cat: dine_api.Category) -> Optional[dine_api.Category]:
    """
    TYPE2: Hybrid stations.
    Filter repetitive items. If no specials left, omit this station.
    """
    cname = norm(cat.name)
    filtered_items = []
    seen = set()

    for item in cat.items:
        n = norm(item.name)
        if n in seen:
            continue
        seen.add(n)

        if cname == "rise and dine" and n in RISE_AND_DINE:
            continue
        if cname == "the stacks" and n in STACKS:
            continue
        if cname == "leaf market" and n in LEAF_MARKET:
            continue
        if cname == "grill house" and n in GRILL_HOUSE:
            continue

        filtered_items.append(item)

    if not filtered_items:
        return None

    return dine_api.Category(id=cat.id, name=cat.name, items=filtered_items)

def _handle_type3_morph(cat: dine_api.Category) -> dine_api.Category:
    """
    TYPE3: Morph stations (Hot Plate, Fresh Bowl, Create).
    Detect what bar type it is today. Return only station title, no items.
    """
    names = [norm(i.name) for i in cat.items]

    # HOT PLATE
    if any(sig in names[:3] for sig in TEPPAN_SIGNATURE):
        station = "Teppenyaki Station"
    elif any(sig in names[:3] for sig in FRENCH_TOAST_SIGNATURE):
        station = "French Toast Bar"
    elif any(sig in names[:3] for sig in PANCAKE_SIGNATURE):
        station = "Pancakes Bar"

    # FRESH BOWL
    elif any(sig in names[:3] for sig in RICE_BOWL_SIGNATURE):
        station = "Rice Bowl"
    elif any(sig in names[:3] for sig in MEZZE_BAR_SIGNATURE):
        station = "Mezze Bar"

    # CREATE
    elif any(sig in names[:3] for sig in RAMEN_BAR_SIGNATURE):
        station = "Ramen Bar"
    elif any(sig in names[:3] for sig in CURRY_BAR_SIGNATURE):
        station = "Curry Bar"
    elif any(sig in names[:3] for sig in PASTA_BAR_SIGNATURE):
        station = "Pasta Bar"

    else:
        station = cat.name  # fallback

    return dine_api.Category(id=cat.id, name=station, items=[])


def extract_specials(periods: Dict[str, dine_api.Period]) -> Dict[str, dine_api.Period]:
    """
    Apply specials filtering logic.
    """
    TYPE3 = {"the hot plate (teppanyaki)", "the hot plate", "fresh bowl", "create"}
    TYPE2 = {"rise and dine", "the stacks", "leaf market", "grill house"}

    out: Dict[str, dine_api.Period] = {}

    for period_key, period in periods.items():
        if not period:
            continue

        new_cats: list[dine_api.Category] = []

        for cat in period.categories:
            cname_norm = norm(cat.name)

            # TYPE3 morph
            if cname_norm in TYPE3:
                new_cat = _handle_type3_morph(cat)
                if new_cat:
                    new_cats.append(new_cat)
                continue

            # TYPE2 hybrid (filter repeats)
            if cname_norm in TYPE2:
                new_cat = _handle_type2_hybrid(cat)
                if new_cat:
                    new_cats.append(new_cat)
                continue

            # TYPE1 (unique) default passthrough
            new_cats.append(_handle_type1_unique(cat))

        out[period_key] = dine_api.Period(
            id=period.id,
            name=period.name,
            sort_order=period.sort_order,
            categories=new_cats,
        )

    return out
