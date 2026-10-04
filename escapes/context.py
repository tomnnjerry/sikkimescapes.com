import re
from urllib.parse import quote

from django.conf import settings

from .content import BANDS, KINDS, LANDS, TIERS, catalogue
from .policies import POLICIES


def _asset_version():
    """Changes whenever a CSS/JS file changes, so browsers never run a stale copy."""
    from pathlib import Path
    root = Path(settings.BASE_DIR) / "static"
    return int(max((p.stat().st_mtime for p in root.rglob("*") if p.suffix in (".css", ".js")), default=0))


def site(request):
    cat = catalogue()
    S = settings.SITE
    regions = list(cat.regions.values())
    phone_digits = re.sub(r"\D", "", S.get("phone", ""))
    wa = re.sub(r"\D", "", S.get("whatsapp", ""))
    popular = []
    for r in regions:  # the cheapest package per district: the affordable promise up front
        js = sorted(r["journeys"], key=lambda j: j.get("price_from_inr", 0))
        if js:
            popular.append(js[0])
    return {
        "SITE": S,
        "nav_regions": regions,
        "nav_themes": list(cat.themes.values()),
        "nav_kinds": [(k, v[0]) for k, v in KINDS.items()],
        "nav_tiers": [dict(v, slug=k, n=len(cat.tier_journeys(k))) for k, v in TIERS.items()],
        "nav_bands": [dict(v, slug=k) for k, v in BANDS.items()],
        "nav_nights": cat.night_counts(),
        "LANDS": LANDS,
        "nav_popular": popular,
        "nav_posts": list(cat.posts.values())[:3],
        "nav_policies": [(k, v["nav"]) for k, v in POLICIES.items()],
        "counts": cat.counts(),
        "canonical": S["url"] + request.path,
        "tel": f"+{phone_digits}" if len(phone_digits) >= 10 else "",
        "wa_base": f"https://wa.me/{wa}" if len(wa) >= 10 else "",
        "wa_text": quote(f"Hello Sikkim Escapes, I would like to plan a Sikkim trip. (Page: {S['url']}{request.path})"),
        "GA4": getattr(settings, "GA4_ID", ""),
        "V": _asset_version(),
    }
