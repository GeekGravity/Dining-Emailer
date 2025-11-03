"""Shared helpers that orchestrate DiningBot's data fetch and email send."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from diningbot.helpers import api as dine_api
from diningbot.helpers import emailer
from diningbot.helpers.period_resolver import DEFAULT_LOCATION_ID, PERIOD_KEYS, resolve_period_ids


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
