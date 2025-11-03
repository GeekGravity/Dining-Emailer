"""HTML rendering utilities for DiningBot."""

from __future__ import annotations

from html import escape
from typing import Dict

from diningbot import api as dine_api


def render_html(date: str, period_map: Dict[str, dine_api.Period]) -> str:  # type: ignore[attr-defined]
    """Return styled HTML for the supplied periods keyed by meal names."""

    def table_section(period_key: str, period: dine_api.Period) -> str:  # type: ignore[attr-defined]
        header = escape(period.name or period_key.title())
        rows: list[str] = [
            "<tr>"
            f"<th colspan=\"2\" style=\"background-color:#1f2937;color:#ffffff;padding:12px 16px;"
            "font-size:18px;text-align:left;border-top-left-radius:12px;border-top-right-radius:12px;\">"
            f"{header}</th></tr>"
        ]

        if period.categories:
            for category in period.categories:
                if not category.items:
                    continue
                cat_name = escape(category.name or "Miscellaneous")
                items_markup: list[str] = []
                for item in category.items:
                    line = escape(item.name or "Unnamed item")
                    if item.description:
                        line += f"<span style=\"color:#5f6368;font-size:13px;\"> - {escape(item.description)}</span>"
                    items_markup.append(f"<li style=\"margin-bottom:6px;\">{line}</li>")
                rows.append(
                    "<tr>"
                    f"<td style=\"vertical-align:top;padding:12px 16px;font-weight:bold;color:#111827;width:32%;"
                    f"background-color:#f1f5f9;\">{cat_name}</td>"
                    f"<td style=\"vertical-align:top;padding:12px 16px;background-color:#ffffff;\">"
                    f"<ul style=\"margin:0;padding-left:18px;color:#303133;\">{''.join(items_markup)}</ul>"
                    "</td>"
                    "</tr>"
                )
        else:
            rows.append(
                "<tr><td colspan=\"2\" style=\"padding:14px 16px;background-color:#ffffff;color:#374151;\">"
                "Menu details are not available for this period.</td></tr>"
            )

        rows.append(
            "<tr><td colspan=\"2\" style=\"height:12px;background-color:#ffffff;border-bottom-left-radius:12px;"
            "border-bottom-right-radius:12px;\"></td></tr>"
        )

        return (
            "<table role=\"presentation\" style=\"width:100%;max-width:640px;margin:0 auto 18px auto;"
            "border-collapse:separate;border-spacing:0;font-family:Arial,Helvetica,sans-serif;"
            "background-color:#ffffff;box-shadow:0 6px 16px rgba(15,23,42,0.1);border-radius:12px;\">"
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
        "<tr><td style=\"font-size:24px;color:#111827;font-weight:bold;\">SFU Dining - "
        f"{escape(date)}</td></tr>"
        "<tr><td style=\"font-size:14px;color:#4b5563;padding-top:6px;\">Daily menu summary</td></tr>"
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
        "<body style=\"margin:0;padding:24px;background-color:#edf2f7;font-family:Arial,Helvetica,sans-serif;\">",
        "  <center style=\"width:100%;\">",
        f"    {header_block}",
        *sections,
        "  </center>",
        "</body>",
        "</html>",
    ]
    return "\n".join(html_parts)
