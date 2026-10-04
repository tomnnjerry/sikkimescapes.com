"""Build content/outlines.json for the self-drawn SVG atlas maps (no map API, no tiles).

Sources (public domain, Natural Earth, https://www.naturalearthdata.com):
- ne_10m_admin_0_countries_ind: country outlines as seen from India's point of view
  (so India's borders follow the official Survey of India depiction).
- ne_10m_admin_1_states_provinces: the Sikkim and West Bengal outlines.
- ne_10m_rivers_lake_centerlines: the Teesta.

Usage: python tools/build_outlines.py   (downloads the two files into .cache/ on first run)
"""
import json
import sys
sys.setrecursionlimit(100000)
import math
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
FILES = {"countries": "ne_10m_admin_0_countries_ind.geojson", "states": "ne_10m_admin_1_states_provinces.geojson",
         "rivers": "ne_10m_rivers_lake_centerlines.geojson"}
COUNTRIES = ["India", "Nepal", "Bhutan", "China"]
KEEP_STATES = {"Sikkim", "West Bengal"}
BOX = (87.3, 26.3, 89.7, 28.7)  # Sikkim and its neighbours: the only window we draw


def fetch(name):
    CACHE.mkdir(exist_ok=True)
    p = CACHE / name
    if not p.exists():
        print("downloading", name)
        urllib.request.urlretrieve(BASE + name, p)
    return json.loads(p.read_text(encoding="utf-8"))


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i]
        d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return rdp(pts[: idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def clip_poly(pts):
    """Sutherland-Hodgman clip of a ring to BOX, so maps carry only what they draw."""
    def clip(poly, inside, cross):
        out = []
        for i, cur in enumerate(poly):
            prev = poly[i - 1]
            if inside(cur):
                if not inside(prev):
                    out.append(cross(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cross(prev, cur))
        return out

    def at_x(x):
        return lambda a, b: (x, a[1] + (b[1] - a[1]) * (x - a[0]) / ((b[0] - a[0]) or 1e-12))

    def at_y(y):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (y - a[1]) / ((b[1] - a[1]) or 1e-12), y)
    x0, y0, x1, y1 = BOX
    for inside, cross in ((lambda p: p[0] >= x0, at_x(x0)), (lambda p: p[0] <= x1, at_x(x1)),
                          (lambda p: p[1] >= y0, at_y(y0)), (lambda p: p[1] <= y1, at_y(y1))):
        pts = clip(pts, inside, cross)
        if not pts:
            return []
    return [(round(x, 3), round(y, 3)) for x, y in pts]


def rings(geom, eps, min_pts=4):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        ring = poly[0]
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        if max(xs) < BOX[0] or min(xs) > BOX[2] or max(ys) < BOX[1] or min(ys) > BOX[3]:
            continue
        pts = clip_poly([(x, y) for x, y in ring])
        if len(pts) < 4:
            continue
        pts.append(pts[0])
        mid = len(pts) // 2  # closed rings start and end on the same point: simplify each half
        simp = rdp(pts[: mid + 1], eps)[:-1] + rdp(pts[mid:], eps)
        if len(simp) >= min_pts:
            out.append(simp)
    return out


def clip_line(coords):
    pts = [(round(x, 3), round(y, 3)) for x, y in coords if BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]]
    return rdp(pts, 0.003) if len(pts) > 1 else []


def main():
    countries = fetch(FILES["countries"])
    states = fetch(FILES["states"])
    rivers = fetch(FILES["rivers"])
    out = {"countries": {}, "states": {}, "rivers": {}}
    for f in countries["features"]:
        name = f["properties"].get("ADMIN")
        if name in COUNTRIES:
            out["countries"][name] = rings(f["geometry"], 0.004)
    for f in states["features"]:
        p = f["properties"]
        if p.get("admin") == "India" and p.get("name") in KEEP_STATES:
            out["states"][p["name"]] = rings(f["geometry"], 0.002)
    for f in rivers["features"]:
        g = f["geometry"]
        if not g:
            continue
        lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        kept = [ln for ln in (clip_line(c) for c in lines) if ln]
        if kept:
            out["rivers"][f["properties"].get("name") or "river"] = kept
    dest = ROOT / "content" / "outlines.json"
    dest.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {dest} · {len(out['countries'])} countries · {len(out['states'])} states · {len(out['rivers'])} rivers · {dest.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
