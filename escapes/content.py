"""In-memory catalogue built from content/*.json.

Every page on the site is rendered from this catalogue. In DEBUG the catalogue
reloads when any content file changes, so writers see edits on refresh.
"""
import json
import re
from collections import OrderedDict
from pathlib import Path

from django.conf import settings
from django.urls import reverse

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTH_SHORT = [m[:3] for m in MONTHS]
REGION_ORDER = ["east-sikkim", "north-sikkim", "west-sikkim", "south-sikkim", "pakyong", "soreng"]
# Each district wears the colours it is known for.
# ground = dark sections, accent = highlights and buttons on dark, ink = accent text on light, tint = light wash,
# grad = 3-stop dark ground gradient, foil = metallic accent (light -> mid -> deep), icon = drawn line icon.
LANDS = {
    "east-sikkim": {"palette": "Monastery maroon and marigold", "short": "Gangtok", "icon": "gompa",
                    "ground": "#4A0F1C", "ground2": "#5E1626", "accent": "#F5A524", "ink": "#93500A", "tint": "#FBEFE4",
                    "grad": ("#2A0710", "#5C1424", "#8A2333"), "foil": ("#FFE3A3", "#F5A524", "#C77A06")},
    "north-sikkim": {"palette": "Glacier night and Gurudongmar turquoise", "short": "Mangan", "icon": "glacier",
                     "ground": "#062B3D", "ground2": "#0A3A52", "accent": "#3FD0C9", "ink": "#0B6964", "tint": "#E2F3F2",
                     "grad": ("#031A26", "#08384F", "#0F5A73"), "foil": ("#CFFFFA", "#3FD0C9", "#12928B")},
    "west-sikkim": {"palette": "Kanchenjunga dawn and silver fir", "short": "Gyalshing", "icon": "summit",
                    "ground": "#0F2E24", "ground2": "#163C30", "accent": "#FF9E6D", "ink": "#AE4517", "tint": "#FCEDE4",
                    "grad": ("#071C15", "#123D30", "#1E5A45"), "foil": ("#FFE0CC", "#FF9E6D", "#D9643A")},
    "south-sikkim": {"palette": "Temi tea and Samdruptse gold", "short": "Namchi", "icon": "tealeaf",
                     "ground": "#1D3511", "ground2": "#284518", "accent": "#E9C046", "ink": "#715800", "tint": "#EEF3E2",
                     "grad": ("#0F200A", "#24451A", "#3A6A26"), "foil": ("#FFF3B8", "#E9C046", "#B88F12")},
    "pakyong": {"palette": "Silk Route indigo and frost lilac", "short": "Silk Route", "icon": "zigzag",
                "ground": "#1C1C4E", "ground2": "#26265F", "accent": "#B7A6FF", "ink": "#5441C2", "tint": "#EEEBFB",
                "grad": ("#0E0E30", "#26266A", "#3E348F"), "foil": ("#EFEAFF", "#B7A6FF", "#7B62E6")},
    "soreng": {"palette": "Barsey rhododendron and cardamom pod", "short": "Soreng", "icon": "rhododendron",
               "ground": "#3A0E22", "ground2": "#4A1430", "accent": "#FF6F7B", "ink": "#B0182C", "tint": "#FCE9EC",
               "grad": ("#22060F", "#4F1230", "#7A1C3F"), "foil": ("#FFD6DA", "#FF6F7B", "#D0283F")},
}

TIERS = OrderedDict([
    ("budget", {"name": "Budget", "label": "Shared jeep and homestays",
                "text": "Clean budget hotels and family homestays, shared or small cars, breakfast and often dinner. The way most people in Sikkim travel."}),
    ("value", {"name": "Value", "label": "Your own car, good 3-star rooms",
               "text": "A private small car and driver, reliable mid-range hotels and the better homestays. The best price-to-comfort ratio."}),
    ("comfort", {"name": "Comfort", "label": "Private SUV, the best mid-range stays",
                 "text": "An Innova or Xylo-class SUV, resorts with views and heating, slower days and a few set pieces."}),
    ("premium", {"name": "Premium", "label": "Top hotels, private everything",
                 "text": "Sikkim's finest hotels, private guides, the best rooms with Kangchenjunga views and the most comfortable vehicles."}),
])

# Price bands for the affordable section (per person, twin sharing)
BANDS = OrderedDict([
    ("under-10000", {"name": "Under ₹10,000", "lo": 0, "hi": 10000}),
    ("10000-20000", {"name": "₹10,000 – 20,000", "lo": 10000, "hi": 20000}),
    ("20000-35000", {"name": "₹20,000 – 35,000", "lo": 20000, "hi": 35000}),
    ("35000-plus", {"name": "Above ₹35,000", "lo": 35000, "hi": 10 ** 9}),
])

KINDS = OrderedDict([
    ("culture", ("Culture", "Palaces, institutes, bazaars and the people who keep them", "Walks through Sikkim's history with people who live it: the Chogyal era, the old trade towns and the communities behind each valley.")),
    ("spiritual", ("Monasteries and shrines", "Gompas, chortens, caves and temples", "Prayer halls at their own hours, mask dances on their own days, and someone to explain what you see.")),
    ("nature", ("Nature", "Lakes, passes, valleys and viewpoints", "Viewpoints at the right hour, alpine lakes and forest days, with altitude and weather taken seriously.")),
    ("wildlife", ("Wildlife and birds", "Red panda country, pheasants and sanctuaries", "Sanctuaries and forest trails timed to season, with local guides who know the calls.")),
    ("food", ("Food", "Momo, thukpa, churpi and farm kitchens", "Kitchens, markets and home tables: the quickest way to understand a valley.")),
    ("adventure", ("Adventure", "Treks, rivers and high roads", "Active days graded honestly by hours, height and terrain, with the right gear and guides.")),
    ("craft", ("Craft", "Weavers, carvers and thangka painters", "Workshops where carpets, choktse tables and thangkas are made. No commission on what you buy.")),
    ("village", ("Village life", "Homestays, farms and harvests", "Nights with families in Lepcha, Bhutia, Limbu, Rai and Sherpa villages, paid fairly and booked directly.")),
    ("wellness", ("Wellness", "Hot springs, quiet and slow days", "Tsachu hot springs, meditation halls and slow mornings with nothing planned.")),
])

_cache = {"stamp": None, "cat": None}


def _read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _stamp(root):
    return max((p.stat().st_mtime for p in root.rglob("*.json")), default=0)


def catalogue():
    root = Path(settings.CONTENT_DIR)
    if _cache["cat"] is None or settings.DEBUG:
        stamp = _stamp(root)
        if stamp != _cache["stamp"]:
            _cache["cat"] = Catalogue(root)
            _cache["stamp"] = stamp
    return _cache["cat"]


def month_bar(best):
    """[{'m': 'Jan', 'v': 2}, ...] for the 12-month strip."""
    best = best or [0] * 12
    return [{"m": MONTH_SHORT[i], "full": MONTHS[i], "v": best[i] if i < len(best) else 0} for i in range(12)]


def best_range(best):
    """'Oct – Mar' style label from a 12-int array (rating 2 = best)."""
    if not best:
        return ""
    good = {i for i, v in enumerate(best) if v == 2} or {i for i, v in enumerate(best) if v >= 1}
    if not good:
        return ""
    if len(good) == 12:
        return "All year"
    runs = []  # runs on a circular calendar, e.g. Oct..Mar
    for i in range(12):
        if i in good and (i - 1) % 12 not in good:
            run, j = [i], (i + 1) % 12
            while j in good:
                run.append(j)
                j = (j + 1) % 12
            runs.append(run)
    labels = []
    for run in runs:
        labels.append(MONTH_SHORT[run[0]] if len(run) == 1 else f"{MONTH_SHORT[run[0]]} – {MONTH_SHORT[run[-1]]}")
    return " · ".join(labels)


class Catalogue:
    def __init__(self, root):
        self.root = root
        self.themes = OrderedDict((t["slug"], t) for t in _read(root / "themes.json"))
        img_file = root / "images.json"
        self.images = _read(img_file) if img_file.exists() else {}
        self.regions = OrderedDict()
        self.places = OrderedDict()
        self.experiences = OrderedDict()
        self.journeys = OrderedDict()
        self.stays = OrderedDict()
        self.guides = OrderedDict()
        self.festivals = OrderedDict()
        self.routes = OrderedDict()
        for slug in REGION_ORDER:
            base = root / slug
            if (base / "region.json").exists():
                self._load_region(slug, base)
        self.posts = OrderedDict()
        for p in (root / "journal").glob("*.json") if (root / "journal").exists() else []:
            d = _read(p)
            d["url"] = reverse("post", args=[d["slug"]])
            self.posts[d["slug"]] = d
        self.posts = OrderedDict(sorted(self.posts.items(), key=lambda kv: kv[1].get("date", ""), reverse=True))
        self._link()
        self._link_posts()

    # ---------- loading ----------
    def _load_region(self, slug, base):
        r = _read(base / "region.json")
        r["slug"] = slug
        pal = LANDS[slug]
        r.update(pal)
        r["pigment"], r["deep"] = pal["accent"], pal["ink"]
        r.setdefault("name", slug.replace("-", " ").title())
        r["url"] = reverse("region", args=[slug])
        r["places"], r["journeys"], r["stays"], r["guides"], r["festivals"], r["routes"] = [], [], [], [], [], []
        self.regions[slug] = r
        for p in sorted((base / "places").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("place", args=[slug, d["slug"]])
            self.places[d["slug"]] = d
            r["places"].append(d)
            for e in d.get("experiences", []):
                e["place"] = d["slug"]
                e["region"] = slug
                e["url"] = reverse("experience", args=[slug, d["slug"], e["slug"]])
                self.experiences[e["slug"]] = e
        for p in sorted((base / "journeys").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("journey", args=[d["slug"]])
            self.journeys[d["slug"]] = d
            r["journeys"].append(d)
        for name, store, key, view in (("stays.json", self.stays, "stays", "stay"),
                                       ("festivals.json", self.festivals, "festivals", "festival"),
                                       ("routes.json", self.routes, "routes", "route")):
            f = base / name
            for d in (_read(f) if f.exists() else []):
                d["region"] = slug
                d["url"] = reverse(view, args=[d["slug"]])
                store[d["slug"]] = d
                r[key].append(d)
        for p in sorted((base / "guides").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("guide", args=[d["slug"]])
            self.guides[d["slug"]] = d
            r["guides"].append(d)

    def _imgs(self, *keys):
        for k in keys:
            if self.images.get(k):
                return self.images[k]
        return []

    def _link(self):
        # drop routes whose places do not exist (yet)
        for slug in [s for s, rt in self.routes.items() if rt.get("from") not in self.places or rt.get("to") not in self.places]:
            dead = self.routes.pop(slug)
            self.regions[dead["region"]]["routes"].remove(dead)
        for r in self.regions.values():
            r["images"] = self._imgs(f"region:{r['slug']}") or [
                i for p in r["places"][:6] for i in self._imgs(f"place:{p['slug']}")[:1]]
            r["best_label"] = best_range(r.get("best_months"))
            r["bar"] = month_bar(r.get("best_months"))
        for p in self.places.values():
            p["region_obj"] = self.regions[p["region"]]
            p["images"] = self._imgs(f"place:{p['slug']}")
            p["best_label"] = best_range(p.get("best_months"))
            p["bar"] = month_bar(p.get("best_months"))
            p["nearby_objs"] = [self.places[s] for s in p.get("nearby", []) if s in self.places]
            p["stay_objs"] = [self.stays[s] for s in p.get("stays", []) if s in self.stays]
            p["journey_objs"] = [j for j in self.journeys.values()
                                 if any(s["place"] == p["slug"] for s in j.get("stops", []))]
            p["festival_objs"] = [f for f in self.festivals.values() if f.get("place") == p["slug"]]
            p["route_objs"] = [rt for rt in self.routes.values() if p["slug"] in (rt.get("from"), rt.get("to"))]
        for r in self.regions.values():
            # the places most journeys stop at lead menus and supply the land's lead photos
            r["top_places"] = sorted(r["places"], key=lambda p: (-len(p["journey_objs"]), p["name"]))
            r["images"] = self._imgs(f"region:{r['slug']}") or [
                i for p in r["top_places"][:6] for i in p["images"][:1]]
        for e in self.experiences.values():
            place = self.places[e["place"]]
            e["place_obj"] = place
            e["region_obj"] = place["region_obj"]
            e["images"] = self._imgs(f"exp:{e['slug']}") or place["images"][1:] or place["images"]
            e["themes"] = place.get("themes", [])
        for s in self.stays.values():
            s["tier_obj"] = TIERS.get(s.get("tier"), TIERS["value"])
            place = self.places.get(s.get("place"))
            s["place_obj"] = place
            s["region_obj"] = self.regions[s["region"]]
            s["images"] = self._imgs(f"stay:{s['slug']}") or (place["images"] if place else [])
            s["journey_objs"] = [j for j in self.journeys.values() if s["slug"] in j.get("stays", [])]
        for j in self.journeys.values():
            j["region_obj"] = self.regions[j["region"]]
            j["tier_obj"] = TIERS.get(j.get("tier"), TIERS["value"])
            j["band"] = next((k for k, b in BANDS.items() if b["lo"] <= (j.get("price_from_inr") or 0) < b["hi"]), "35000-plus")
            j["per_night"] = round((j.get("price_from_inr") or 0) / max(1, j.get("nights") or 1), -1)
            stops = [dict(st, obj=self.places[st["place"]]) for st in j.get("stops", []) if st["place"] in self.places]
            j["stop_objs"] = stops
            j["images"] = self._imgs(f"journey:{j['slug']}") or [
                i for st in stops for i in st["obj"]["images"][:1]]
            j["stay_objs"] = [self.stays[s] for s in j.get("stays", []) if s in self.stays]
            j["best_label"] = best_range(j.get("best_months"))
            j["bar"] = month_bar(j.get("best_months"))
            j["days_count"] = j.get("nights", 0) + 1
            for d in j.get("days", []):
                d["place_obj"] = self.places.get(d.get("place"))
            j["profile"] = [{"day": d.get("day"), "alt": d.get("alt_m") or 0, "name": d.get("overnight") or (d.get("place_obj") or {}).get("name", "")}
                            for d in j.get("days", [])]
            j["districts"] = sorted({st["obj"]["region"] for st in stops}, key=REGION_ORDER.index)
        for g in self.guides.values():
            g["region_obj"] = self.regions[g["region"]]
            rel = [self.places[s] for s in g.get("related_places", []) if s in self.places]
            g["related_objs"] = rel
            g["images"] = self._imgs(f"guide:{g['slug']}") or [i for p in rel for i in p["images"][:1]] or g["region_obj"]["images"]
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in g.get("sections", []))
            g["read_min"] = max(3, round(words / 220))
            for s in g.get("sections", []):
                s["anchor"] = re.sub(r"[^a-z0-9]+", "-", s.get("heading", "").lower()).strip("-")
        for f in self.festivals.values():
            place = self.places.get(f.get("place"))
            f["place_obj"] = place
            f["region_obj"] = self.regions[f["region"]]
            f["images"] = self._imgs(f"fest:{f['slug']}") or (place["images"] if place else [])
        for rt in self.routes.values():
            rt["from_obj"] = self.places.get(rt.get("from"))
            rt["to_obj"] = self.places.get(rt.get("to"))
            rt["region_obj"] = self.regions[rt["region"]]
            rt["images"] = (rt["to_obj"] or {}).get("images", []) + (rt["from_obj"] or {}).get("images", [])[:1]
        for t in self.themes.values():
            t["url"] = reverse("theme", args=[t["slug"]])

    def _link_posts(self):
        from datetime import date
        for d in self.posts.values():
            d["region_objs"] = [self.regions[r] for r in d.get("regions", []) if r in self.regions]
            d["journey_objs"] = [self.journeys[j] for j in d.get("related_journeys", []) if j in self.journeys]
            d["place_objs"] = [self.places[x] for x in d.get("related_places", []) if x in self.places]
            d["images"] = (self._imgs(f"blog:{d['slug']}") or [i for x in d["place_objs"] for i in x["images"][:1]])
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in d.get("sections", []))
            d["read_min"] = max(3, round(words / 220))
            d["cat_slug"] = re.sub(r"[^a-z0-9]+", "-", d.get("category", "").lower()).strip("-")
            try:
                d["date_obj"] = date.fromisoformat(d.get("date", ""))
            except ValueError:
                d["date_obj"] = None
            land = d["region_objs"][0]["slug"] if d["region_objs"] else None
            d["land"] = land
            stores = {"journey": self.journeys, "place": self.places, "stay": self.stays, "guide": self.guides, "festival": self.festivals}
            for sec in d.get("sections", []):
                sec["anchor"] = re.sub(r"[^a-z0-9]+", "-", sec.get("heading", "").lower()).strip("-")
                objs = []
                for ln in sec.get("links", []):
                    o = stores.get(ln.get("type"), {}).get(ln.get("slug"))
                    if o:
                        objs.append({"type": ln["type"], "title": o.get("title") or o.get("name"), "url": o["url"],
                                     "img": (o.get("images") or [None])[0]})
                sec["link_objs"] = objs
        self.post_categories = OrderedDict()
        for d in self.posts.values():
            self.post_categories.setdefault(d["cat_slug"], {"slug": d["cat_slug"], "name": d.get("category"), "posts": []})["posts"].append(d)

    # ---------- queries ----------
    def theme_items(self, theme, region=None):
        def ok(x):
            return region is None or x.get("region") == region
        places = [p for p in self.places.values() if theme in p.get("themes", []) and ok(p)]
        journeys = [j for j in self.journeys.values() if theme in j.get("themes", []) and ok(j)]
        place_slugs = {p["slug"] for p in places}
        stays = [s for s in self.stays.values() if s.get("place") in place_slugs and ok(s)]
        experiences = [e for e in self.experiences.values() if e["place"] in place_slugs and ok(e)]
        return {"places": places, "journeys": journeys, "stays": stays, "experiences": experiences}

    def region_theme_pairs(self):
        """(region, theme) pairs with enough content to deserve a page."""
        out = []
        for r in self.regions:
            for t in self.themes:
                items = self.theme_items(t, r)
                if len(items["places"]) >= 2 and (items["journeys"] or len(items["places"]) >= 3):
                    out.append((r, t))
        return out

    def region_kind_pairs(self):
        """(region, kind) pairs with at least 3 experiences."""
        out = []
        for r in self.regions:
            for k in KINDS:
                if sum(1 for e in self.experiences.values() if e["region"] == r and e.get("kind") == k) >= 3:
                    out.append((r, k))
        return out

    # ---------- commerce and story queries ----------
    def band_journeys(self, band):
        b = BANDS[band]
        return sorted([j for j in self.journeys.values() if b["lo"] <= (j.get("price_from_inr") or 0) < b["hi"]],
                      key=lambda j: j.get("price_from_inr") or 0)

    def tier_journeys(self, tier, region=None):
        return sorted([j for j in self.journeys.values() if j.get("tier") == tier and (region is None or j["region"] == region)],
                      key=lambda j: j.get("price_from_inr") or 0)

    def night_counts(self):
        """Trip lengths (nights) with at least two packages, for /packages/<n>-nights/ pages."""
        from collections import Counter
        c = Counter(j.get("nights") for j in self.journeys.values())
        return sorted(n for n, k in c.items() if n and k >= 2)

    def stories(self):
        out = []
        for p in self.places.values():
            if (p.get("story") or {}).get("text"):
                out.append({"title": p["story"].get("title") or p["name"], "text": p["story"]["text"],
                            "source": p["story"].get("source", ""), "obj": p, "url": p["url"] + "#story"})
        return out

    def little_known(self):
        out = []
        for p in self.places.values():
            for f in p.get("little_known", []) or []:
                if f.get("fact"):
                    out.append(dict(f, obj=p))
        return out

    def ladder(self):
        return sorted([p for p in self.places.values() if isinstance(p.get("altitude_m"), int)], key=lambda p: p["altitude_m"])

    def counts(self):
        return {
            "regions": len(self.regions), "places": len(self.places), "experiences": len(self.experiences),
            "journeys": len(self.journeys), "stays": len(self.stays), "guides": len(self.guides),
            "festivals": len(self.festivals), "routes": len(self.routes), "themes": len(self.themes),
            "posts": len(self.posts),
        }

    def all_images(self):
        seen, out = set(), []
        for key, recs in self.images.items():
            for rec in recs:
                if rec["file"] not in seen:
                    seen.add(rec["file"])
                    out.append(dict(rec, used_for=key))
        return out
