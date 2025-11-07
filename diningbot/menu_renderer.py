"""HTML rendering utilities for DiningBot."""

from __future__ import annotations

from html import escape
from typing import Dict

from diningbot import fetch_helper as dine_api


def render_html(date: str, period_map: Dict[str, dine_api.Period]) -> str:  # type: ignore[attr-defined]
    """Return styled HTML for the supplied periods keyed by meal names."""

    # Palette
    OUTER_BG = "#141313"
    CONTAINER_BG = "#1B1A19"
    BORDER = "#6B5E4B" 
    ACCENT = "#D7B47E"   
    H1_COLOR = "#E9DFC8"   
    TEXT = "#D9D4C7"       
    MUTED = "#C8C3B6"       
    TINTS = {
        "breakfast": "#D7B47E",  # golden beige
        "lunch": "#6B5E4B",      # coffee grey-brown
        "dinner": "#2B2122",     # deep plum-brown
    }

    def table_section(period_key: str, period: dine_api.Period) -> str:  # type: ignore[attr-defined]
        """Return a dark-themed section for one meal period."""
        header = escape(period.name or period_key.title())
        tint = TINTS.get(period_key.lower(), BORDER)

        rows: list[str] = []

        # Section header (thin divider + label)
        rows.append(
            "<tr>"
            f"<td style=\"padding:18px 0 8px 0;border-top:1px solid {BORDER};\">"
            f"<h2 style=\"margin:0;font-family:Georgia,'Times New Roman',serif;"
            f"font-size:20px;line-height:26px;color:{H1_COLOR};font-weight:600;"
            f"letter-spacing:0.2px;text-align:left;\">"
            # tinted pill before header text
            f"<span style=\"display:inline-block;width:10px;height:10px;border-radius:50%;"
            f"background:{tint};vertical-align:middle;margin-right:10px;\"></span>"
            f"{header}"
            f"</h2>"
            "</td>"
            "</tr>"
        )

        if period.categories:
            for category in period.categories:
                cat_name = escape(category.name or "Miscellaneous")

                # Category subheading
                rows.append(
                    "<tr>"
                    f"<td style=\"padding:10px 0 4px 0;\">"
                    f"<div style=\"display:inline-block;padding:6px 10px;border:1px solid {BORDER};"
                    f"border-radius:14px;color:{MUTED};font-family:'Helvetica Neue',Arial,sans-serif;"
                    f"font-size:12px;line-height:16px;\">{cat_name}</div>"
                    "</td>"
                    "</tr>"
                )

                # Items list
                items_markup = []
                for item in category.items:
                    text = escape(item.name or "Unnamed item")
                    if item.description:
                        text += (
                            f" <span style='color:{MUTED};font-size:12px;'>"
                            f"- {escape(item.description)}</span>"
                        )
                    items_markup.append(f"• {text}")

                rows.append(
                    "<tr>"
                    f"<td style=\"vertical-align:top;padding:6px 0 10px 0;"
                    f"color:{TEXT};font-family:'Helvetica Neue',Arial,sans-serif;"
                    f"font-size:14px;line-height:22px;\">{'<br>'.join(items_markup)}</td>"
                    "</tr>"
                )
        else:
            rows.append(
                "<tr>"
                f"<td style=\"padding:10px 0;color:{TEXT};font-family:'Helvetica Neue',Arial,sans-serif;"
                "font-size:14px;line-height:22px;\">"
                "Menu details are not available for this period."
                "</td>"
                "</tr>"
            )

        return "".join(rows)

    # Build all period sections (order preserved; no functional changes)
    sections = [
        table_section(key, period)
        for key, period in period_map.items()
        if period
    ]

    # Header block: “Today's Specials” (no date, no hero)
    header_block = (
        "<tr>"
        f"<td style=\"padding:24px 20px 12px 20px;background-color:{CONTAINER_BG};\">"
        f"<h1 style=\"margin:0;font-family:Georgia,'Times New Roman',serif;font-size:28px;line-height:34px;"
        f"color:{H1_COLOR};font-weight:700;text-align:center;\">Today's Specials</h1>"
        "</td>"
        "</tr>"
    )

    # Optional top utility line (right-aligned)
    view_in_browser = (
        "<tr>"
        f"<td style=\"padding:10px 16px;background-color:{CONTAINER_BG};border-bottom:1px solid {BORDER};\">"
        f"<p style=\"margin:0;font-family:'Helvetica Neue',Arial,sans-serif;font-size:12px;line-height:18px;"
        f"color:{TEXT};text-align:right;\">"
        "</p>"
        "</td>"
        "</tr>"
    )

    # Inner content table (holds all sections)
    inner_content = (
        "<tr>"
        f"<td style=\"padding:0 24px 24px 24px;background-color:{CONTAINER_BG};\">"
        "<table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" width=\"100%\" "
        "style=\"border-collapse:separate;border-spacing:0;\">"
        f"{''.join(sections) if sections else ''}"
        "</table>"
        "</td>"
        "</tr>"
    )

    # Outer container (gold border card on dark background)
    container_table = (
        "<table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" width=\"100%\" "
        f"style=\"max-width:600px;width:100%;background-color:{CONTAINER_BG};border:1px solid {BORDER};\">"
        f"{view_in_browser}"
        f"{header_block}"
        # (No hero image row by design)
        f"{inner_content}"
        # Footer divider (subtle)
        "<tr>"
        f"<td style=\"padding:0 24px;background-color:{CONTAINER_BG};\">"
        "<table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" width=\"100%\">"
        f"<tr><td style=\"border-top:1px solid {BORDER};line-height:0;font-size:0;\">&nbsp;</td></tr>"
        "</table>"
        "</td>"
        "</tr>"
        "</table>"
    )

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"utf-8\">",
        "  <meta http-equiv=\"x-ua-compatible\" content=\"ie=edge\">",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        "  <meta name=\"color-scheme\" content=\"only dark\">",
        "  <meta name=\"supported-color-schemes\" content=\"dark\">",
        f"  <title>SFU Dining - {escape(date)}</title>",
        "</head>",
        # Full-width dark background + centered container
        f"<body style=\"margin:0;padding:24px;background-color:{OUTER_BG};"
        "font-family:Arial,Helvetica,sans-serif;\">",
        "  <center style=\"width:100%;\">",
        f"    {container_table}",
        # Breathing room spacer for small screens
        "    <table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" width=\"100%\" "
        "style=\"max-width:600px;\">"
        "      <tr><td style=\"line-height:1px;font-size:1px;\">&nbsp;</td></tr>"
        "    </table>",
        "  </center>",
        "</body>",
        "</html>",
    ]

    return "\n".join(html_parts)
