import json
from datetime import date

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .content import BANDS, KINDS, LANDS, MONTH_SHORT, MONTHS, TIERS, catalogue, month_bar
from .forms import EnquiryForm, SubscribeForm
from .models import Subscriber
from .policies import POLICIES, UPDATED

COMPANY_FAQS = [
    {"q": "What does Sikkim Escapes do?",
     "a": "We plan trips in Sikkim only, from shared-jeep budget escapes and village homestays to private comfort and premium tours. We handle permits through registered partners, book the cars and rooms, and give you one person to call from Bagdogra or NJP until you are back on the plains."},
    {"q": "Are your package prices fixed?",
     "a": "No. Prices on the site are indicative 'from' prices in INR per person, twin sharing, and each package shows how the price breaks down. The final quote depends on dates, group size, room category and availability. We send a written, itemised quote before you pay anything."},
    {"q": "How cheap can a Sikkim trip be?",
     "a": "A Gangtok weekend with shared jeeps and a budget hotel can cost under ₹10,000 per person from NJP. A 5–6 night trip with North Sikkim usually starts around ₹13,000–20,000 per person on a budget. Our Affordable section lists every package by price band, with the real costs of jeeps, rooms and permits."},
    {"q": "Do you arrange permits for North Sikkim, Nathu La and the Silk Route?",
     "a": "Yes. These permits are issued only through Sikkim Tourism-registered agents and vehicles, and we apply through registered partners with your ID and photos, usually a day ahead. Nathu La and the Silk Route are for Indian nationals only. Rules change often, so check current status before you travel."},
    {"q": "Can foreigners travel with you?",
     "a": "Yes, with limits. Foreign nationals need a Restricted Area Permit (now online through e-FRRO) to enter Sikkim, and can visit some protected areas such as Tsomgo and Lachung–Yumthang in groups of two or more. Nathu La, Gurudongmar and Zuluk are closed to foreigners. Check current status before you travel."},
    {"q": "Can you change a package?",
     "a": "Yes, and most people do. The packages on the site show routes that work. We change hotels, add nights, move up or down a tier, or combine districts, then send a new day-by-day plan with the new price."},
    {"q": "When is the best time to visit Sikkim?",
     "a": "March to May for rhododendrons and clear spring days, and October to December for the clearest mountain views. December to March brings snow up high. June to September is monsoon: cheaper, green and quieter, but landslides close roads, especially NH10 and North Sikkim."},
    {"q": "Where do your photos come from?",
     "a": "Every photo on this site comes from Wikimedia Commons under a free licence. We name the author and licence under each photo and list all of them, with links to the originals, on our photo credits page."},
    {"q": "Is travel insurance included?",
     "a": "No. We ask every traveller to hold insurance that covers medical treatment and evacuation, including at the altitudes on your route (Gurudongmar is above 5,000 m). If you have heart or lung conditions, speak to your doctor before booking a high-altitude trip."},
]


def ld(*items):
    """Render JSON-LD blocks safely."""
    return [json.dumps(i, ensure_ascii=False).replace("</", "<\\/") for i in items]


def crumbs(*pairs):
    items = [("Home", reverse("home"))] + list(pairs)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": settings.SITE["url"] + u}
        for i, (n, u) in enumerate(items)]}
    return items, data


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]}


def img_url(obj):
    imgs = obj.get("images") or []
    return imgs[0]["thumb"] if imgs else None


def org_ld():
    s = settings.SITE
    return {"@context": "https://schema.org", "@type": "TravelAgency", "name": s["name"], "url": s["url"],
            "areaServed": {"@type": "State", "name": "Sikkim"}}


def _get(store, slug):
    obj = store.get(slug)
    if not obj:
        raise Http404
    return obj


def _month_now():
    return date.today().month - 1


# ---------------- home and indexes ----------------
def home(request):
    cat = catalogue()
    regions = list(cat.regions.values())
    m = _month_now()
    tiers = []
    for k, tv in TIERS.items():
        js = cat.tier_journeys(k)
        tiers.append({"slug": k, **tv, "journeys": js[:4], "from": js[0]["price_from_inr"] if js else None})
    bands = [{"slug": k, **b, "n": len(cat.band_journeys(k)), "first": (cat.band_journeys(k) or [None])[0]} for k, b in BANDS.items()]
    cheapest = sorted(cat.journeys.values(), key=lambda j: j.get("price_from_inr") or 0)[:4]
    in_season = [p for p in cat.places.values() if (p.get("best_months") or [0] * 12)[m] == 2]
    in_season = sorted(in_season, key=lambda p: -len(p["journey_objs"]))[:8]
    fests = [f for f in cat.festivals.values() if (m + 1) in f.get("month_nums", []) or ((m + 1) % 12 + 1) in f.get("month_nums", [])][:4]
    facts = cat.little_known()
    facts = facts[::max(1, len(facts) // 10)][:10] if facts else []
    stories = cat.stories()
    stories = stories[::max(1, len(stories) // 6)][:6] if stories else []
    climb = [cat.places[s] for s in ("melli", "namchi", "gangtok", "pelling", "lachung", "tsomgo-lake", "nathang-valley", "gurudongmar-lake") if s in cat.places]
    return render(request, "escapes/home.html", {
        "regions": regions, "tiers": tiers, "bands": bands, "cheapest": cheapest, "month": MONTHS[m], "month_i": m,
        "in_season": in_season, "festivals": fests, "facts": facts, "stories": stories, "climb": climb,
        "guides": [g for g in cat.guides.values() if g.get("category") in ("money", "stories")][:4],
        "themes": list(cat.themes.values()), "months_short": MONTH_SHORT, "months_full": MONTHS,
        "posts": list(cat.posts.values())[:3],
        "ld": ld(org_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": settings.SITE["name"], "url": settings.SITE["url"],
                            "potentialAction": {"@type": "SearchAction", "target": settings.SITE["url"] + "/?q={q}", "query-input": "required name=q"}}),
    })


def lands(request):
    cat = catalogue()
    items, bc = crumbs(("Districts", reverse("lands")))
    return render(request, "escapes/lands.html", {"regions": list(cat.regions.values()), "crumbs": items,
                                                "months_short": MONTH_SHORT, "ld": ld(bc)})


def region(request, region):
    cat = catalogue()
    r = _get(cat.regions, region)
    items, bc = crumbs(("Districts", reverse("lands")), (r["name"], r["url"]))
    exps = [e for p in r["places"] for e in p.get("experiences", [])[:1]]
    styles = [cat.themes[t] for (rr, t) in cat.region_theme_pairs() if rr == region]
    months = [{"name": MONTHS[i], "slug": MONTHS[i].lower(), "rating": (r.get("best_months") or [0] * 12)[i],
               "weather": (r.get("months") or [{}] * 12)[i].get("weather", "") if i < len(r.get("months", [])) else ""}
              for i in range(12)]
    place_ld = {"@context": "https://schema.org", "@type": "TouristDestination", "name": r["name"],
                "description": r.get("summary"), "url": settings.SITE["url"] + r["url"],
                "includesAttraction": [{"@type": "TouristAttraction", "name": p["name"]} for p in r["places"]]}
    return render(request, "escapes/region.html", {
        "r": r, "crumbs": items, "experiences": exps, "styles": styles, "months": months,
        "kinds": [(k, KINDS[k][0]) for rr, k in cat.region_kind_pairs() if rr == region],
        "ld": ld(bc, place_ld, faq_ld(r.get("faqs", []))),
        "map_points": json.dumps([{"name": p["name"], "lat": p.get("lat"), "lng": p.get("lng"), "url": p["url"],
                                   "kind": p.get("kind", "")} for p in r["places"] if p.get("lat")]),
    })


def region_month(request, region, month):
    cat = catalogue()
    r = _get(cat.regions, region)
    names = [m.lower() for m in MONTHS]
    if month not in names:
        raise Http404
    i = names.index(month)
    md = r.get("months", [])[i] if i < len(r.get("months", [])) else {}
    go = [cat.places[s] for s in md.get("go", []) if s in cat.places]
    events = [cat.festivals[s] for s in md.get("events", []) if s in cat.festivals]
    journeys = [j for j in r["journeys"] if (j.get("best_months") or [0] * 12)[i] == 2]
    rating = (r.get("best_months") or [0] * 12)[i]
    others = [{"r": rr, "rating": (rr.get("best_months") or [0] * 12)[i]} for rr in cat.regions.values() if rr["slug"] != region]
    items, bc = crumbs(("Districts", reverse("lands")), (r["name"], r["url"]), (f"{MONTHS[i]}", request.path))
    title = f"{r['name']} in {MONTHS[i]}"
    faqs = [
        {"q": f"Is {MONTHS[i]} a good time to visit {r['name']}?",
         "a": (md.get("summary") or "")[:600] or f"See our month-by-month notes for {r['name']}."},
        {"q": f"What is the weather like in {r['name']} in {MONTHS[i]}?",
         "a": f"{md.get('weather', 'Weather varies across the region')}. Conditions differ by altitude and coast, so check the forecast for each stop a week before you travel."},
        {"q": f"Where should we go in {r['name']} in {MONTHS[i]}?",
         "a": ("We suggest " + ", ".join(p["name"] for p in go) + ". " if go else "") + (md.get("tip") or "")},
    ]
    return render(request, "escapes/region_month.html", {
        "r": r, "i": i, "month": MONTHS[i], "md": md, "go": go, "events": events, "journeys": journeys,
        "rating": rating, "others": others, "crumbs": items, "title": title, "faqs": faqs,
        "prev": names[(i - 1) % 12], "next": names[(i + 1) % 12], "prev_name": MONTHS[(i - 1) % 12], "next_name": MONTHS[(i + 1) % 12],
        "ld": ld(bc, faq_ld(faqs)),
    })


def region_theme(request, region, theme):
    cat = catalogue()
    r = _get(cat.regions, region)
    t = _get(cat.themes, theme)
    if (region, theme) not in cat.region_theme_pairs():
        raise Http404
    data = cat.theme_items(theme, region)
    items, bc = crumbs(("Districts", reverse("lands")), (r["name"], r["url"]), (t["name"], request.path))
    return render(request, "escapes/region_theme.html", {"r": r, "t": t, **data, "crumbs": items, "ld": ld(bc)})


def place(request, region, place):
    cat = catalogue()
    p = _get(cat.places, place)
    if p["region"] != region:
        return redirect(p["url"], permanent=True)
    r = p["region_obj"]
    items, bc = crumbs(("Districts", reverse("lands")), (r["name"], r["url"]), (p["name"], p["url"]))
    dest = {"@context": "https://schema.org", "@type": "TouristDestination", "name": p["name"],
            "description": p.get("summary"), "url": settings.SITE["url"] + p["url"], "image": img_url(p)}
    if p.get("lat"):
        dest["geo"] = {"@type": "GeoCoordinates", "latitude": p["lat"], "longitude": p["lng"]}
    return render(request, "escapes/place.html", {
        "p": p, "r": r, "crumbs": items, "ld": ld(bc, dest, faq_ld(p.get("faqs", []))),
        "map_points": json.dumps([{"name": x["name"], "lat": x.get("lat"), "lng": x.get("lng"), "url": x["url"], "main": x is p}
                                  for x in [p] + p["nearby_objs"] if x.get("lat")]),
    })


def experience(request, region, place, exp):
    cat = catalogue()
    e = _get(cat.experiences, exp)
    p = e["place_obj"]
    if p["slug"] != place or e["region"] != region:
        return redirect(e["url"], permanent=True)
    r = e["region_obj"]
    siblings = [x for x in p.get("experiences", []) if x is not e]
    items, bc = crumbs(("Districts", reverse("lands")), (r["name"], r["url"]), (p["name"], p["url"]), (e["title"], e["url"]))
    attraction = {"@context": "https://schema.org", "@type": "TouristAttraction", "name": e["title"],
                  "description": e.get("summary"), "image": img_url(e),
                  "containedInPlace": {"@type": "Place", "name": p["name"]}}
    return render(request, "escapes/experience.html", {
        "e": e, "p": p, "r": r, "siblings": siblings, "crumbs": items,
        "ld": ld(bc, attraction, faq_ld(e.get("faqs", []))),
    })


def journeys(request):
    cat = catalogue()
    items, bc = crumbs(("Packages", reverse("journeys")))
    return render(request, "escapes/journeys.html", {"journeys": list(cat.journeys.values()), "regions": list(cat.regions.values()),
                                                   "themes": list(cat.themes.values()), "crumbs": items, "ld": ld(bc)})


def journey(request, slug):
    cat = catalogue()
    j = _get(cat.journeys, slug)
    r = j["region_obj"]
    items, bc = crumbs(("Packages", reverse("journeys")), (j["title"], j["url"]))
    trip = {"@context": "https://schema.org", "@type": "TouristTrip", "name": j["title"], "description": j.get("summary"),
            "image": img_url(j), "touristType": [cat.themes[t]["name"] for t in j.get("themes", []) if t in cat.themes],
            "itinerary": {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": {"@type": "Place", "name": s["obj"]["name"]}}
                for i, s in enumerate(j["stop_objs"])]},
            "offers": {"@type": "Offer", "priceCurrency": "INR", "price": j.get("price_from_inr"),
                       "description": "Indicative price per person, twin sharing"}}
    related = [x for x in r["journeys"] if x is not j][:3]
    return render(request, "escapes/journey.html", {
        "j": j, "r": r, "crumbs": items, "related": related,
        "ld": ld(bc, trip, faq_ld(j.get("faqs", []))),
        "map_points": json.dumps([{"name": s["obj"]["name"], "lat": s["obj"].get("lat"), "lng": s["obj"].get("lng"),
                                   "url": s["obj"]["url"], "nights": s["nights"]} for s in j["stop_objs"] if s["obj"].get("lat")]),
    })


def stays(request):
    cat = catalogue()
    items, bc = crumbs(("Stays", reverse("stays")))
    return render(request, "escapes/stays.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def stay(request, slug):
    cat = catalogue()
    s = _get(cat.stays, slug)
    items, bc = crumbs(("Stays", reverse("stays")), (s["name"], s["url"]))
    hotel = {"@context": "https://schema.org", "@type": "Hotel", "name": s["name"], "description": s.get("summary"),
             "image": img_url(s), "address": {"@type": "PostalAddress", "addressLocality": (s.get("place_obj") or {}).get("name", "")}}
    if s.get("website"):
        hotel["sameAs"] = s["website"]
    others = [x for x in s["region_obj"]["stays"] if x is not s][:3]
    return render(request, "escapes/stay.html", {"s": s, "crumbs": items, "others": others,
                                               "ld": ld(bc, hotel, faq_ld(s.get("faqs", [])))})


def experiences(request):
    cat = catalogue()
    items, bc = crumbs(("Experiences", reverse("experiences")))
    kinds = sorted({e.get("kind", "") for e in cat.experiences.values() if e.get("kind")})
    return render(request, "escapes/experiences.html", {"regions": list(cat.regions.values()), "kinds": kinds,
                                                      "kind_links": [(k, v[0]) for k, v in KINDS.items()],
                                                      "count": len(cat.experiences), "crumbs": items, "ld": ld(bc)})


def _kind_page(request, kind, region=None):
    cat = catalogue()
    if kind not in KINDS:
        raise Http404
    name, tagline, intro = KINDS[kind]
    exps = [e for e in cat.experiences.values() if e.get("kind") == kind and (region is None or e["region"] == region)]
    r = cat.regions.get(region) if region else None
    if region and (not r or (region, kind) not in cat.region_kind_pairs()):
        raise Http404
    trail = [("Experiences", reverse("experiences"))]
    if r:
        trail = [("Districts", reverse("lands")), (r["name"], r["url"]), (f"{name} experiences", request.path)]
    else:
        trail.append((name, request.path))
    items, bc = crumbs(*trail)
    lands = [cat.regions[rr] for rr, k in cat.region_kind_pairs() if k == kind]
    others = [(k, v[0]) for k, v in KINDS.items() if k != kind and (region is None or (region, k) in cat.region_kind_pairs())]
    return render(request, "escapes/experience_kind.html", {
        "kind": kind, "name": name, "tagline": tagline, "intro": intro, "exps": exps, "r": r,
        "lands": lands, "others": others, "crumbs": items, "ld": ld(bc)})


def experience_kind(request, kind):
    return _kind_page(request, kind)


def region_kind(request, region, kind):
    return _kind_page(request, kind, region)


def guides(request):
    cat = catalogue()
    items, bc = crumbs(("Guides", reverse("guides")))
    return render(request, "escapes/guides.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def guide(request, slug):
    cat = catalogue()
    g = _get(cat.guides, slug)
    r = g["region_obj"]
    items, bc = crumbs(("Guides", reverse("guides")), (g["title"], g["url"]))
    article = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g.get("summary"),
               "image": img_url(g), "author": {"@type": "Organization", "name": settings.SITE["byline"]},
               "publisher": {"@type": "Organization", "name": settings.SITE["name"]}}
    more = [x for x in r["guides"] if x is not g][:3]
    return render(request, "escapes/guide.html", {"g": g, "r": r, "crumbs": items, "more": more,
                                                "ld": ld(bc, article, faq_ld(g.get("faqs", [])))})


def festivals(request):
    cat = catalogue()
    items, bc = crumbs(("Festivals", reverse("festivals")))
    by_month = []
    for i, m in enumerate(MONTHS):
        fs = [f for f in cat.festivals.values() if (i + 1) in f.get("month_nums", [])]
        by_month.append({"name": m, "festivals": fs})
    return render(request, "escapes/festivals.html", {"by_month": by_month, "count": len(cat.festivals), "crumbs": items, "ld": ld(bc)})


def festival(request, slug):
    cat = catalogue()
    f = _get(cat.festivals, slug)
    items, bc = crumbs(("Festivals", reverse("festivals")), (f["name"], f["url"]))
    journeys = [j for j in f["region_obj"]["journeys"] if "festivals" in j.get("themes", [])][:3]
    return render(request, "escapes/festival.html", {"f": f, "crumbs": items, "journeys": journeys,
                                                   "bar": month_bar([2 if (i + 1) in f.get("month_nums", []) else 0 for i in range(12)]),
                                                   "ld": ld(bc, faq_ld(f.get("faqs", [])))})


def routes(request):
    cat = catalogue()
    items, bc = crumbs(("Routes", reverse("routes")))
    return render(request, "escapes/routes.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def route(request, slug):
    cat = catalogue()
    rt = _get(cat.routes, slug)
    if not (rt["from_obj"] and rt["to_obj"]):
        raise Http404
    items, bc = crumbs(("Routes", reverse("routes")), (f"{rt['from_obj']['name']} to {rt['to_obj']['name']}", rt["url"]))
    pts = [x for x in (rt["from_obj"], rt["to_obj"]) if x and x.get("lat")]
    return render(request, "escapes/route.html", {"rt": rt, "crumbs": items, "ld": ld(bc, faq_ld(rt.get("faqs", []))),
                                                "map_points": json.dumps([{"name": x["name"], "lat": x["lat"], "lng": x["lng"], "url": x["url"]} for x in pts])})


def themes(request):
    cat = catalogue()
    items, bc = crumbs(("Themes", reverse("themes")))
    rows = [{"t": t, "n": len(cat.theme_items(t["slug"])["journeys"])} for t in cat.themes.values()]
    return render(request, "escapes/themes.html", {"rows": rows, "crumbs": items, "ld": ld(bc)})


def theme(request, slug):
    cat = catalogue()
    t = _get(cat.themes, slug)
    data = cat.theme_items(slug)
    pairs = [cat.regions[r] for (r, tt) in cat.region_theme_pairs() if tt == slug]
    items, bc = crumbs(("Themes", reverse("themes")), (t["name"], t["url"]))
    return render(request, "escapes/theme.html", {"t": t, **data, "region_pages": pairs, "crumbs": items, "ld": ld(bc)})


def seasons(request):
    cat = catalogue()
    items, bc = crumbs(("Seasons", reverse("seasons")))
    return render(request, "escapes/seasons.html", {"regions": list(cat.regions.values()), "months": MONTHS,
                                                  "months_short": MONTH_SHORT, "crumbs": items, "ld": ld(bc)})


# ---------------- tools ----------------
def tools(request):
    items, bc = crumbs(("Trip tools", reverse("tools")))
    return render(request, "escapes/tools.html", {"crumbs": items, "ld": ld(bc)})


def tool_season(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Season finder", reverse("tool_season")))
    data = [{"n": p["name"], "u": p["url"], "r": p["region_obj"]["name"], "rs": p["region"], "b": p.get("best_months") or [0] * 12,
             "k": p.get("kind", ""), "i": (p["images"][0]["thumb"] if p["images"] else "")} for p in cat.places.values()]
    return render(request, "escapes/tool_season.html", {"crumbs": items, "data": json.dumps(data).replace("</", "<\\/"), "months": MONTHS, "ld": ld(bc),
                                                      "regions": list(cat.regions.values()), "now": _month_now()})


def tool_budget(request):
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Trip cost calculator", reverse("tool_budget")))
    return render(request, "escapes/tool_budget.html", {"crumbs": items, "ld": ld(bc), "regions": list(catalogue().regions.values())})


def tool_permits(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Permits", reverse("tool_permits")))
    return render(request, "escapes/tool_permits.html", {"crumbs": items, "ld": ld(bc), "regions": list(cat.regions.values())})


# ---------------- enquiry ----------------
def plan(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("plan_thanks")
    else:
        initial = {"source_page": request.GET.get("from", "")[:300], "kind": "full"}
        if request.GET.get("land"):
            initial["lands"] = [request.GET["land"]]
        if request.GET.get("month") in MONTHS:
            initial["month"] = request.GET["month"]
        if request.GET.get("journey"):
            initial["message"] = f"I am interested in: {request.GET['journey'][:150]}"
        form = EnquiryForm(initial=initial)
    items, bc = crumbs(("Plan a trip", reverse("plan")))
    return render(request, "escapes/plan.html", {"form": form, "crumbs": items, "ld": ld(bc)})


def plan_thanks(request):
    return render(request, "escapes/plan_thanks.html", {"crumbs": crumbs(("Plan a trip", reverse("plan")))[0]})


# ---------------- static and utility ----------------
def old_policy(request, page):
    return redirect("policy", slug={"privacy": "privacy", "terms": "booking-terms"}[page], permanent=True)


def static_page(request, page):
    titles = {"about": "About us", "privacy": "Privacy", "terms": "Terms"}
    items, bc = crumbs((titles[page], request.path))
    return render(request, f"escapes/{page}.html", {"crumbs": items, "counts": catalogue().counts(), "ld": ld(bc)})


def faq(request):
    cat = catalogue()
    items, bc = crumbs(("FAQ", reverse("faq")))
    groups = [{"name": "Travelling with us", "faqs": COMPANY_FAQS}] + [
        {"name": r["name"], "faqs": r.get("faqs", []), "url": r["url"]} for r in cat.regions.values()]
    return render(request, "escapes/faq.html", {"groups": groups, "crumbs": items, "ld": ld(bc, faq_ld(COMPANY_FAQS))})


def photo_credits(request):
    cat = catalogue()
    items, bc = crumbs(("Photo credits", reverse("photo_credits")))
    return render(request, "escapes/photo_credits.html", {"images": cat.all_images(), "crumbs": items, "ld": ld(bc)})


def html_sitemap(request):
    cat = catalogue()
    items, bc = crumbs(("Sitemap", reverse("html_sitemap")))
    return render(request, "escapes/sitemap.html", {"cat": cat, "regions": list(cat.regions.values()), "crumbs": items,
                                                  "pairs": [(cat.regions[r], cat.themes[t]) for r, t in cat.region_theme_pairs()],
                                                  "kind_pairs": [(cat.regions[r], k, KINDS[k][0]) for r, k in cat.region_kind_pairs()],
                                                  "month_slugs": [(m, m.lower()) for m in MONTHS], "ld": ld(bc)})


def robots(request):
    body = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /plan/thank-you/\n\nSitemap: {settings.SITE['url']}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain")


def llms(request):
    cat = catalogue()
    lines = [f"# {settings.SITE['name']}", "",
             "> Sikkim-only trips from shared-jeep budget escapes to premium tours, with honest prices, permits and rooted local stories.", ""]
    for r in cat.regions.values():
        lines.append(f"## {r['name']}")
        lines.append(f"- [{r['name']} overview]({settings.SITE['url']}{r['url']}): {r.get('summary', '')}")
        for p in r["places"]:
            lines.append(f"- [{p['name']}]({settings.SITE['url']}{p['url']}): {p.get('summary', '')}")
        for j in r["journeys"]:
            lines.append(f"- [{j['title']}]({settings.SITE['url']}{j['url']}): {j.get('summary', '')}")
        lines.append("")
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def not_found(request, exception=None):
    return render(request, "escapes/404.html", {"crumbs": []}, status=404)
