"""HTML rendering utilities for DiningBot."""

from __future__ import annotations

from html import escape
from typing import Dict

from diningbot.helpers import api as dine_api


def render_html(date: str, period_map: Dict[str, dine_api.Period]) -> str:  # type: ignore[attr-defined]
    """Return styled HTML for the supplied periods keyed by meal names."""

    def table_section(period_key: str, period: dine_api.Period) -> str:  # type: ignore[attr-defined]
        header = escape(period.name or period_key.title())

        # pick soft color per period
        accent = {
            "breakfast": "#ffedd5",  # peach
            "lunch": "#e0f2fe",       # sky
            "dinner": "#ede9fe"       # lavender
        }.get(period_key.lower(), "#e5e7eb")

        rows: list[str] = [
            "<tr>"
            f"<th style=\"background-color:{accent};color:#1f2937;padding:14px 0;"
            "font-size:18px;text-align:center;border-top-left-radius:10px;border-top-right-radius:10px;\">"
            f"{header}</th></tr>"
        ]

        if period.categories:
            for category in period.categories:
                if not category.items:
                    continue
                cat_name = escape(category.name or "Miscellaneous")

                # station subheading row
                rows.append(
                    "<tr><td style=\"padding:14px 0 8px 0;background-color:#ffffff;"
                    "color:#111827;font-size:15px;font-weight:bold;text-align:center;border-top:1px solid #e5e7eb;\">"
                    f"{cat_name}"
                    "</td></tr>"
                )

                # bullet item list
                items_markup = []
                for item in category.items:
                    text = escape(item.name or "Unnamed item")
                    if item.description:
                        text += f" <span style='color:#6b7280;font-size:12px;'>- {escape(item.description)}</span>"
                    items_markup.append(f"• {text}")

                rows.append(
                    "<tr>"
                    f"<td style=\"vertical-align:top;padding:8px 18px;background-color:#ffffff;color:#303133;"
                    f"font-size:15px;line-height:1.4;\">{'<br>'.join(items_markup)}</td>"
                    "</tr>"
                )
        else:
            rows.append(
                "<tr><td style=\"padding:14px 16px;background-color:#ffffff;color:#374151;\">"
                "Menu details are not available for this period.</td></tr>"
            )

        rows.append(
            "<tr><td style=\"height:10px;background-color:#ffffff;border-bottom-left-radius:10px;"
            "border-bottom-right-radius:10px;\"></td></tr>"
        )

        return (
            "<table role=\"presentation\" style=\"width:100%;max-width:720px;margin:0 auto 26px auto;"
            "border-collapse:separate;border-spacing:0;font-family:Arial,Helvetica,sans-serif;"
            "background-color:#ffffff;border-radius:10px;border:1px solid #e5e7eb;\">"
            f"{''.join(rows)}"
            "</table>"
        )

    sections = [
        table_section(key, period)
        for key, period in period_map.items()
        if period
    ]

    header_block = (
        "<table role=\"presentation\" style=\"margin:0 auto 24px auto;text-align:center;\">"
        "<tr><td style=\"font-size:22px;color:#111827;font-weight:bold;text-align:center;\">SFU Dining - "
        f"{escape(date)}</td></tr>"
        "<tr><td style=\"font-size:13px;color:#4b5563;padding-top:4px;text-align:center;\">Daily menu summary</td></tr>"
        "</table>"
    )

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"utf-8\">",
        "  <meta http-equiv=\"x-ua-compatible\" content=\"ie=edge\">",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        f"  <title>SFU Dining - {escape(date)}</title>",
        "</head>",
        "<body style=\"margin:0;padding:24px;background-color:#f0f9ff;font-family:Arial,Helvetica,sans-serif;\">",
        "  <center style=\"width:100%;\">",
        f"    {header_block}",
        *sections,
        "  </center>",
        "</body>",
        "</html>",
    ]

    return "\n".join(html_parts)
