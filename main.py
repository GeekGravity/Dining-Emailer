"""DiningBot entry point that fetches today's menu and emails it."""

from __future__ import annotations

import datetime as _dt
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv

from diningbot import api as dine_api
from diningbot import emailer
from diningbot.menu_renderer import render_html
from diningbot.period_resolver import DEFAULT_LOCATION_ID, PERIOD_KEYS, resolve_period_ids

_logger = logging.getLogger(__name__)


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

    subject = f"SFU Dining - {date}"
    plain_text = build_plain_text(subject, periods)
    emailer.send_email(settings, subject, html_output, plain_text)


def main() -> int:
    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    date = _dt.date.today().isoformat()
    try:
        periods = fetch_daily_periods(date)
    except RuntimeError as exc:
        _logger.error("Failed to fetch periods for %s: %s", date, exc)
        return 1

    html_output = render_html(date, periods)

    try:
        send_menu_email(date, html_output, periods)
    except RuntimeError as exc:
        _logger.error("%s", exc)
        return 1
    except Exception as exc:  # pragma: no cover - network side effects
        _logger.error("Failed to send email: %s", exc)
        return 1

    _logger.info("Dining menu email sent for %s", date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
