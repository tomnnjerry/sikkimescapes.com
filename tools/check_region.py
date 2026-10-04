"""Validate one region's content against content/SCHEMA.md.

Usage: python tools/check_region.py <region-slug> [--wiki]
--wiki also confirms every `wiki` title exists on English Wikipedia.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content"
THEMES = set("monasteries lakes-and-passes snow-and-winter flowers-and-forests village-homestays honeymoons "
             "family-holidays treks-and-walks food-and-tea festivals birds-and-wildlife photography "
             "crafts-and-culture offbeat-sikkim".split())
TIERS = {"budget", "value", "comfort", "premium"}
KINDS = set("culture nature wildlife food adventure spiritual craft village wellness".split())
MASTER = json.loads((Path(__file__).resolve().parent.parent / "content" / "_places.json").read_text(encoding="utf-8"))["districts"]
ALL_MASTER = {s for d in MASTER.values() for s in d["places"]}
BANNED = ["nestled", "breathtaking", "hidden gem", "paradise", "tapestry", "embark", "delve", "unleash",
          "vibrant", "bustling", "mesmeriz", "stunning", "magical", "heaven on earth", "feast for the eyes",
          "something for everyone", "whether you're", "look no further", "ultimate guide", "in this blog",
          "in conclusion", "unforgettable", "world-class", "seamless", "elevate", "immerse", "timeless",
          "boasts", "abode of peace", "land of mystic", "switzerland of", "offbeat gem", "must-visit",
          "bucket list", "shangri-la", "curated", "jewel", "!"]
errors, warns = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(p, f"invalid JSON ({e})")
        return None


def months(where, v):
    if not (isinstance(v, list) and len(v) == 12 and all(x in (0, 1, 2) for x in v)):
        err(where, "best_months must be 12 ints of 0/1/2")


def faqs(where, v, n):
    if not isinstance(v, list) or len(v) != n:
        err(where, f"needs exactly {n} faqs (has {len(v) if isinstance(v, list) else 0})")
        return
    for f in v:
        if not f.get("q") or not f.get("a"):
            err(where, "faq missing q/a")


def heading(where, t):
    if t and t.rstrip().endswith("."):
        err(where, f"heading ends with full stop: {t!r}")


def scan_banned(where, obj):
    text = json.dumps(obj, ensure_ascii=False).lower()
    for b in BANNED:
        if b in text:
            warns.append(f"{where}: banned word/phrase '{b}'")


def main():
    r = sys.argv[1]
    base = ROOT / r
    wiki_titles = []
    reg = load(base / "region.json")
    places, stays, fests = {}, {}, {}
    for p in sorted((base / "places").glob("*.json")):
        d = load(p)
        if d:
            places[d["slug"]] = d
    known = set(ALL_MASTER)
    for pdir in ROOT.iterdir():
        if pdir.is_dir() and (pdir / "places").exists():
            known |= {q.stem for q in (pdir / "places").glob("*.json")}
    known |= set(places)
    for s in load(base / "stays.json") or []:
        stays[s["slug"]] = s
    for f in load(base / "festivals.json") or []:
        fests[f["slug"]] = f

    for must in MASTER.get(r, {}).get("places", {}):
        if must not in places:
            err("master list", f"missing required place '{must}'")
    for slug, d in places.items():
        if slug != Path(slug).stem or not (base / "places" / f"{slug}.json").exists():
            err(f"place {slug}", "file name must equal slug")
    if reg:
        months("region", reg.get("best_months"))
        if len(reg.get("little_known", [])) != 5:
            err("region", "needs 5 little_known")
        if not (reg.get("story") or {}).get("source"):
            err("region", "story needs text and source")
        faqs("region", reg.get("faqs"), 9)
        if len(reg.get("highlights", [])) != 6:
            err("region", "needs 6 highlights")
        if len(reg.get("months", [])) != 12:
            err("region", "needs 12 months")
        for m in reg.get("months", []):
            for g in m.get("go", []):
                if g not in known:
                    err(f"region month {m.get('month')}", f"unknown place '{g}'")
            for e in m.get("events", []):
                if e not in fests:
                    err(f"region month {m.get('month')}", f"unknown festival '{e}'")
        wiki_titles.append(reg.get("wiki"))
        scan_banned("region", reg)

    exp_slugs = set()
    for slug, d in places.items():
        w = f"place {slug}"
        months(w, d.get("best_months"))
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("tagline"))
        for t in d.get("themes", []):
            if t not in THEMES:
                err(w, f"unknown theme '{t}'")
        if not isinstance(d.get("altitude_m"), int):
            err(w, "altitude_m must be int")
        if len(d.get("little_known", [])) != 3:
            err(w, "needs 3 little_known")
        if not (d.get("story") or {}).get("source"):
            err(w, "story needs text and source")
        if not 4 <= len(d.get("costs", [])) <= 6:
            err(w, "needs 4-6 costs rows")
        for n in d.get("nearby", []):
            if n not in known:
                err(w, f"unknown nearby '{n}'")
        for s in d.get("stays", []):
            if s not in stays:
                err(w, f"unknown stay '{s}'")
        ex = d.get("experiences", [])
        if len(ex) != 4:
            err(w, f"needs 4 experiences (has {len(ex)})")
        for e in ex:
            heading(f"{w} exp", e.get("title"))
            if e.get("kind") not in KINDS:
                err(w, f"unknown experience kind {e.get('kind')!r}")
            faqs(f"{w} exp {e.get('slug')}", e.get("faqs"), 3)
            if e["slug"] in exp_slugs:
                err(w, f"duplicate experience slug {e['slug']}")
            exp_slugs.add(e["slug"])
            if e.get("wiki"):
                wiki_titles.append(e["wiki"])
        wiki_titles.append(d.get("wiki"))
        scan_banned(w, d)

    for p in sorted((base / "journeys").glob("*.json")):
        d = load(p)
        if not d:
            continue
        w = f"journey {d.get('slug')}"
        months(w, d.get("best_months"))
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("title"))
        if d.get("tier") not in TIERS:
            err(w, f"bad tier {d.get('tier')!r}")
        pb = sum(x[1] for x in d.get("price_breakdown", []))
        pr = d.get("price_from_inr") or 0
        if not pr or abs(pb - pr) > pr * 0.05:
            err(w, f"price_breakdown sums to {pb}, price_from_inr is {pr}")
        for dy in d.get("days", []):
            if not isinstance(dy.get("alt_m"), int):
                err(w, f"day {dy.get('day')} needs int alt_m")
        total = sum(s.get("nights", 0) for s in d.get("stops", []))
        if total != d.get("nights"):
            err(w, f"stop nights {total} != nights {d.get('nights')}")
        if len(d.get("days", [])) != d.get("nights", 0) + 1:
            err(w, "days must equal nights + 1")
        for s in d.get("stops", []):
            if s["place"] not in known:
                err(w, f"unknown stop '{s['place']}'")
        for s in d.get("stays", []):
            if s not in stays:
                err(w, f"unknown stay '{s}'")
        for t in d.get("themes", []):
            if t not in THEMES:
                err(w, f"unknown theme '{t}'")
        scan_banned(w, d)

    for slug, s in stays.items():
        w = f"stay {slug}"
        faqs(w, s.get("faqs"), 3)
        if s.get("tier") not in TIERS:
            err(w, f"bad tier {s.get('tier')!r}")
        if s.get("place") not in known:
            err(w, f"unknown place '{s.get('place')}'")
        if s.get("wiki"):
            wiki_titles.append(s["wiki"])
        scan_banned(w, s)

    for p in sorted((base / "guides").glob("*.json")):
        d = load(p)
        if not d:
            continue
        w = f"guide {d.get('slug')}"
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("title"))
        words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in d.get("sections", []))
        if words < 1000:
            warns.append(f"{w}: only {words} words")
        for s in d.get("sections", []):
            heading(w, s.get("heading"))
        for rp in d.get("related_places", []):
            if rp not in known:
                err(w, f"unknown related place '{rp}'")
        scan_banned(w, d)

    for slug, f in fests.items():
        w = f"festival {slug}"
        faqs(w, f.get("faqs"), 4)
        if f.get("place") not in places:
            err(w, f"unknown place '{f.get('place')}'")
        if f.get("wiki"):
            wiki_titles.append(f["wiki"])
        scan_banned(w, f)

    for rt in load(base / "routes.json") or []:
        w = f"route {rt.get('slug')}"
        faqs(w, rt.get("faqs"), 4)
        for k in ("from", "to"):
            if rt.get(k) not in known:
                err(w, f"unknown {k} '{rt.get(k)}'")
        scan_banned(w, rt)

    if "--wiki" in sys.argv:
        titles = sorted({t for t in wiki_titles if t})
        for i in range(0, len(titles), 40):
            q = urllib.parse.urlencode({"action": "query", "titles": "|".join(titles[i:i + 40]),
                                        "redirects": 1, "format": "json", "formatversion": 2})
            req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q,
                                         headers={"User-Agent": "SikkimEscapesBuild/1.0"})
            data = json.load(urllib.request.urlopen(req, timeout=30))
            for pg in data["query"]["pages"]:
                if pg.get("missing"):
                    err("wiki", f"no Wikipedia article titled {pg['title']!r} (use '' or fix)")

    counts = (f"places={len(places)} experiences={len(exp_slugs)} stays={len(stays)} festivals={len(fests)} "
              f"journeys={len(list((base / 'journeys').glob('*.json')))} guides={len(list((base / 'guides').glob('*.json')))}")
    print(counts)
    for w in warns:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
