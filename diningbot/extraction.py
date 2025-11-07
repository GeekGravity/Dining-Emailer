from typing import Dict, Optional
from diningbot import fetch_helper as dine_api
from diningbot.repeated_values import (
    norm,
    RISE_AND_DINE,
    STACKS,
    LEAF_MARKET,
    GRILL_HOUSE,
    TEPPAN_SIGNATURE,
    SHAWARMA_SIGNATURE,
    FRENCH_TOAST_SIGNATURE,
    PANCAKE_SIGNATURE,
    RICE_BOWL_SIGNATURE,
    MEZZE_BAR_SIGNATURE,
    RAMEN_BAR_SIGNATURE,
    CURRY_BAR_SIGNATURE,
    PASTA_BAR_SIGNATURE,
)

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
    elif any(sig in names[:3] for sig in SHAWARMA_SIGNATURE):
        station = "Shawarma Station"
    elif any(sig in names[:3] for sig in FRENCH_TOAST_SIGNATURE):
        station = "French Toast Bar"
    elif any(sig in names[:3] for sig in PANCAKE_SIGNATURE):
        station = "Pancakes Bar"

    # FRESH BOWL
    elif any(sig in names[:3] for sig in RICE_BOWL_SIGNATURE):
        station = "Rice Bowl Bar"
    elif any(sig in names[:3] for sig in MEZZE_BAR_SIGNATURE):
        station = "Mezze Bar"

    # CREATE
    elif any(sig in names[:3] for sig in RAMEN_BAR_SIGNATURE):
        station = "Ramen Station"
    elif any(sig in names[:3] for sig in CURRY_BAR_SIGNATURE):
        station = "Curry Station"
    elif any(sig in names for sig in PASTA_BAR_SIGNATURE):
        station = "Pasta Station"

    else:
        station = cat.name  # fallback

    return dine_api.Category(id=cat.id, name=station, items=[])


def extract_specials(periods: Dict[str, dine_api.Period]) -> Dict[str, dine_api.Period]:
    """
    Apply specials filtering logic.

    MODIFIED RULES:
      - BREAKFAST: keep only Rise & Dine
      - TYPE3: station name stays as header + classification appears as single bullet item
      - TYPE3 should always appear at the bottom of the period
    """
    TYPE3 = {"the hot plate (teppanyaki)", "the hot plate", "fresh bowl", "create"}
    TYPE2 = {"rise and dine", "the stacks", "leaf market", "grill house"}

    out: Dict[str, dine_api.Period] = {}

    for period_key, period in periods.items():
        if not period:
            continue

        type1_and_type2: list[dine_api.Category] = []
        type3_list: list[dine_api.Category] = []

        for cat in period.categories:
            cname_norm = norm(cat.name)

            if cname_norm in TYPE3:
                morph = _handle_type3_morph(cat)
                # classification = morph.name (station classification we detected)
                classification = morph.name
                # make bullet item object using same class
                item_cls = cat.items[0].__class__
                type3_list.append(
                    dine_api.Category(
                        id=cat.id,
                        name=cat.name,  # original station name
                        items=[ item_cls(classification, None) ]
                    )
                )
                continue

            # TYPE2 hybrid (remove repeats)
            if cname_norm in TYPE2:
                new_cat = _handle_type2_hybrid(cat)
                if new_cat:
                    type1_and_type2.append(new_cat)
                continue

            # TYPE1 passthrough
            type1_and_type2.append(_handle_type1_unique(cat))

        # merge in final order: TYPE1+TYPE2 then TYPE3 at end
        new_cats = type1_and_type2 + type3_list

        # BREAKFAST filter: only Rise & Dine
        if period_key.lower() == "breakfast":
            new_cats = [c for c in new_cats if norm(c.name) == "rise and dine"]

        out[period_key] = dine_api.Period(
            id=period.id,
            name=period.name,
            sort_order=period.sort_order,
            categories=new_cats,
        )

    return out
