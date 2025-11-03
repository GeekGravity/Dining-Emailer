"""DiningBot entry point that fetches today's menu and emails it."""

import datetime as _dt
import logging

from dotenv import load_dotenv

from diningbot.helpers.menu_renderer import render_html
from diningbot.menu_service import fetch_daily_periods, send_menu_email

_logger = logging.getLogger(__name__)


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
    print(html_output)

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
