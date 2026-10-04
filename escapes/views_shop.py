"""The affordable section, package filters, statewide seasons, stories and the altitude ladder."""
import json

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from .content import BANDS, LANDS, MONTHS, TIERS, catalogue
from .views import crumbs, faq_ld, ld


def _item_list(name, objs):
    return {"@context": "https://schema.org", "@type": "ItemList", "name": name, "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": settings.SITE["url"] + o["url"], "name": o.get("title") or o.get("name")}
        for i, o in enumerate(objs[:30])]}


def _cost_rows(cat, region=None):
    rows = []
    for p in cat.places.values():
        if region and p["region"] != region:
            continue
        for label, value in (p.get("costs") or [])[:6]:
            rows.append({"label": label, "value": value, "place": p})
    return rows


AFFORDABLE_FAQS = [
    {"q": "What is the cheapest way to travel around Sikkim?",
     "a": "Shared jeeps and Sikkim Nationalised Transport buses. Shared jeeps run from Siliguri and NJP to Gangtok, Namchi, Jorethang and Pelling, and from Gangtok to Mangan and the north, priced per seat. Pair them with homestays at ₹1,200–2,500 per person including meals and a week can cost far less than a private tour."},
    {"q": "Can we do North Sikkim on a budget?",
     "a": "Yes. North Sikkim is visited on permit packages from Gangtok that include a shared or reserved vehicle, a basic room and meals for two or three nights. Budget versions start at roughly ₹6,500–9,000 per person. You cannot drive your own car or travel without a registered agent. Check current status before you travel."},
    {"q": "Are budget hotels in Sikkim clean and safe?",
     "a": "The ones we use are. Budget rooms in Lachung, Lachen and Zuluk are simple, often with shared heating and limited hot water, but clean. In Gangtok and Pelling budget hotels are better equipped. We tell you exactly what a room has before you book."},
    {"q": "When is Sikkim cheapest?",
     "a": "June to mid-September (monsoon) and mid-January to February, outside the New Year week. Hotels discount and roads are quieter. Monsoon brings landslides, so keep a buffer day. October, the Puja holidays, Christmas and New Year are the most expensive weeks."},
    {"q": "What costs do people forget?",
     "a": "The ₹50 Sikkim tourist entry fee collected at hotels, protected-area permits, Zero Point extra cab charges, porter and guide tips, room heaters, and the drive back to Bagdogra or NJP on your last day. Each of our packages shows its price breakdown so none of these surprise you."},
    {"q": "Is your budget tier a group tour?",
     "a": "Not usually. Budget trips are private to your party with a smaller car and simpler rooms. For North Sikkim, shared-vehicle packages are cheaper still; we tell you when your trip uses a shared vehicle and who else might ride with you."},
]


def affordable(request):
    cat = catalogue()
    items, bc = crumbs(("Affordable Sikkim", reverse("affordable")))
    bands = [{"slug": k, **b, "journeys": cat.band_journeys(k)} for k, b in BANDS.items()]
    budget_stays = [s for s in cat.stays.values() if s.get("tier") == "budget"]
    money = [g for g in cat.guides.values() if g.get("category") == "money"]
    costs = _cost_rows(cat)
    regions = []
    for r in cat.regions.values():
        js = sorted(r["journeys"], key=lambda j: j.get("price_from_inr") or 0)
        regions.append({"r": r, "from": js[0]["price_from_inr"] if js else None, "cheapest": js[:1]})
    return render(request, "escapes/affordable.html", {
        "bands": bands, "budget_stays": budget_stays[:12], "money": money, "costs": costs[::max(1, len(costs) // 24)][:24],
        "regions": regions, "faqs": AFFORDABLE_FAQS, "crumbs": items,
        "ld": ld(bc, faq_ld(AFFORDABLE_FAQS), _item_list("Affordable Sikkim packages", cat.band_journeys("under-10000") + cat.band_journeys("10000-20000")))})


def band(request, band):
    cat = catalogue()
    if band not in BANDS:
        raise Http404
    b = BANDS[band]
    js = cat.band_journeys(band)
    items, bc = crumbs(("Affordable Sikkim", reverse("affordable")), (f"Packages {b['name']}", request.path))
    others = [{"slug": k, **v} for k, v in BANDS.items() if k != band]
    lo = min((j["price_from_inr"] for j in js), default=None)
    faqs = [
        {"q": f"What does a Sikkim trip {b['name'].lower()} per person include?",
         "a": "Every package in this band lists its price breakdown: rooms, the car and driver, permits and fees, and our planning fee. Prices are indicative per person, twin sharing, and change with dates and group size. We send a written, itemised quote before you pay."},
        {"q": "Can we bring the price down further?",
         "a": "Yes: travel in a group of four to six to share the car, choose homestays over hotels, travel outside October and the New Year week, and use shared jeeps for the long transfers. Tell us your budget and we will build around it."},
        {"q": "Are flights or trains included?",
         "a": "No. Prices start and end at Bagdogra Airport (IXB) or New Jalpaiguri station (NJP). Pakyong airport has no scheduled flights at present. Check current status before you travel."},
    ]
    return render(request, "escapes/band.html", {"b": b, "band": band, "journeys": js, "others": others, "lo": lo,
                                                 "faqs": faqs, "crumbs": items,
                                                 "ld": ld(bc, faq_ld(faqs), _item_list(f"Sikkim packages {b['name']}", js))})


def tier(request, tier):
    cat = catalogue()
    if tier not in TIERS:
        raise Http404
    tv = TIERS[tier]
    js = cat.tier_journeys(tier)
    stays = [s for s in cat.stays.values() if s.get("tier") == tier]
    items, bc = crumbs(("Packages", reverse("journeys")), (f"{tv['name']} packages", request.path))
    others = [{"slug": k, **v} for k, v in TIERS.items() if k != tier]
    return render(request, "escapes/tier.html", {"tier": tier, "tv": tv, "journeys": js, "stays": stays, "others": others,
                                                 "regions": list(cat.regions.values()), "crumbs": items,
                                                 "ld": ld(bc, _item_list(f"{tv['name']} Sikkim packages", js))})


def nights(request, n):
    cat = catalogue()
    if n not in cat.night_counts():
        raise Http404
    js = sorted([j for j in cat.journeys.values() if j.get("nights") == n], key=lambda j: j.get("price_from_inr") or 0)
    items, bc = crumbs(("Packages", reverse("journeys")), (f"{n} nights", request.path))
    lengths = [x for x in cat.night_counts() if x != n]
    return render(request, "escapes/nights.html", {"n": n, "days": n + 1, "journeys": js, "lengths": lengths,
                                                   "crumbs": items, "ld": ld(bc, _item_list(f"{n} night Sikkim packages", js))})


def homestays(request):
    cat = catalogue()
    stays = [s for s in cat.stays.values() if "homestay" in (s.get("kind") or "") or s.get("kind") == "farmstay"]
    places = [p for p in cat.places.values() if "village-homestays" in p.get("themes", [])]
    items, bc = crumbs(("Stays", reverse("stays")), ("Homestays", request.path))
    t = cat.themes.get("village-homestays")
    return render(request, "escapes/homestays.html", {"stays": stays, "places": places, "t": t, "crumbs": items,
                                                      "ld": ld(bc, _item_list("Sikkim homestays", stays))})


def region_budget(request, region):
    cat = catalogue()
    r = cat.regions.get(region)
    if not r:
        raise Http404
    js = sorted([j for j in r["journeys"] if j.get("tier") in ("budget", "value")], key=lambda j: j.get("price_from_inr") or 0)
    stays = [s for s in r["stays"] if s.get("tier") in ("budget", "value")]
    money = [g for g in r["guides"] if g.get("category") == "money"]
    items, bc = crumbs(("Districts", reverse("lands")), (r["name"], r["url"]), ("On a budget", request.path))
    lo = js[0]["price_from_inr"] if js else None
    faqs = [
        {"q": f"How much does a budget trip to {r['name']} cost?",
         "a": (r.get("money") or "")[:700] or f"Our cheapest {r['name']} packages are listed on this page with full price breakdowns."},
        {"q": f"What is the cheapest way to get around {r['name']}?",
         "a": "Shared jeeps between towns, priced per seat, and a reserved small car for sightseeing days. Protected areas need a registered vehicle and permit. The cost table on this page shows indicative fares; check current status before you travel."},
        {"q": f"Where can we stay cheaply in {r['name']}?",
         "a": ("Budget and value options we use: " + ", ".join(s["name"] for s in stays[:5]) + ". ") if stays else "Village homestays usually cost ₹1,200–2,500 per person with meals; we book registered ones directly."},
    ]
    return render(request, "escapes/region_budget.html", {"r": r, "journeys": js, "stays": stays, "money": money, "lo": lo,
                                                          "costs": _cost_rows(cat, region), "faqs": faqs, "crumbs": items,
                                                          "ld": ld(bc, faq_ld(faqs), _item_list(f"{r['name']} budget packages", js))})


def sikkim_month(request, month):
    cat = catalogue()
    names = [m.lower() for m in MONTHS]
    if month not in names:
        raise Http404
    i = names.index(month)
    rows = []
    for r in cat.regions.values():
        md = r.get("months", [])[i] if i < len(r.get("months", [])) else {}
        rows.append({"r": r, "md": md, "rating": (r.get("best_months") or [0] * 12)[i],
                     "go": [cat.places[s] for s in md.get("go", []) if s in cat.places]})
    journeys = sorted([j for j in cat.journeys.values() if (j.get("best_months") or [0] * 12)[i] == 2],
                      key=lambda j: j.get("price_from_inr") or 0)
    fests = [f for f in cat.festivals.values() if (i + 1) in f.get("month_nums", [])]
    items, bc = crumbs(("Seasons", reverse("seasons")), (f"Sikkim in {MONTHS[i]}", request.path))
    best = [x["r"]["name"] for x in rows if x["rating"] == 2]
    avoid = [x["r"]["name"] for x in rows if x["rating"] == 0]
    faqs = [
        {"q": f"Is {MONTHS[i]} a good time to visit Sikkim?",
         "a": (f"In {MONTHS[i]} the best districts are {', '.join(best)}. " if best else f"{MONTHS[i]} is a shoulder or off month across most of Sikkim. ")
         + (f"Avoid or plan carefully for {', '.join(avoid)}. " if avoid else "") + "Weather and road status change year to year: check current status before you travel."},
        {"q": f"What is the weather in Sikkim in {MONTHS[i]}?",
         "a": " ".join(f"{x['r']['name']}: {x['md'].get('weather')}." for x in rows if x["md"].get("weather"))[:700] or "It varies sharply with altitude."},
        {"q": f"Are hotels cheaper in Sikkim in {MONTHS[i]}?",
         "a": "Rates are lowest in the monsoon (June to mid-September) and in late January and February. They peak in October, around Christmas and New Year, and in May and early June when plains holidays begin. Book the peak weeks early."},
    ]
    return render(request, "escapes/sikkim_month.html", {"i": i, "month": MONTHS[i], "rows": rows, "journeys": journeys[:8],
                                                         "festivals": fests, "faqs": faqs, "crumbs": items,
                                                         "prev": names[(i - 1) % 12], "next": names[(i + 1) % 12],
                                                         "prev_name": MONTHS[(i - 1) % 12], "next_name": MONTHS[(i + 1) % 12],
                                                         "months": [(m, m.lower()) for m in MONTHS],
                                                         "ld": ld(bc, faq_ld(faqs))})


def stories(request):
    cat = catalogue()
    items, bc = crumbs(("Rooted stories", reverse("stories")))
    groups = []
    for r in cat.regions.values():
        st = [s for s in cat.stories() if s["obj"]["region"] == r["slug"]]
        groups.append({"r": r, "stories": st})
    guides = [g for g in cat.guides.values() if g.get("category") == "stories"]
    return render(request, "escapes/stories.html", {"groups": groups, "facts": cat.little_known(), "guides": guides,
                                                    "region_stories": [r for r in cat.regions.values() if (r.get("story") or {}).get("text")],
                                                    "crumbs": items, "ld": ld(bc)})


def altitude(request):
    cat = catalogue()
    items, bc = crumbs(("The altitude ladder", reverse("altitude")))
    ladder = cat.ladder()
    return render(request, "escapes/altitude.html", {"ladder": ladder, "top": max((p["altitude_m"] for p in ladder), default=8586),
                                                     "crumbs": items, "ld": ld(bc)})


def tool_altitude(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Altitude check", request.path))
    data = [{"t": j["title"], "u": j["url"], "n": j["nights"], "tier": j.get("tier"), "p": j["profile"],
             "max": j.get("max_altitude_m")} for j in cat.journeys.values()]
    return render(request, "escapes/tool_altitude.html", {"crumbs": items, "ld": ld(bc),
                                                          "data": json.dumps(data, ensure_ascii=False).replace("</", "<\\/")})
