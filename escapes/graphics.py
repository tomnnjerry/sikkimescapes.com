"""Server-drawn SVG graphics for the "Milestone" design: contour lines and altitude profiles.

Nothing here calls out to a service. Contours are seeded from a slug, so every page gets its own
terrain and keeps it between visits.
"""
import hashlib
import math
import random

from django.utils.html import escape


def _rng(seed):
    return random.Random(int(hashlib.md5(str(seed).encode()).hexdigest()[:8], 16))


def contour_svg(seed, rings=14, cls="contour", peaks=2, labels=True, base_alt=1000, step_alt=200):
    """Topographic contour lines around one to three peaks, as an SVG that covers its box."""
    rnd = _rng(seed)
    W, H = 1200, 700
    out = [f'<svg class="{cls}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">']
    for pk in range(peaks):
        cx = rnd.uniform(0.2, 0.85) * W
        cy = rnd.uniform(0.25, 0.8) * H
        phases = [rnd.uniform(0, math.tau) for _ in range(4)]
        amps = [rnd.uniform(0.05, 0.16), rnd.uniform(0.03, 0.1), rnd.uniform(0.02, 0.06), rnd.uniform(0.01, 0.04)]
        stretch = rnd.uniform(0.7, 1.35)
        n = rings if pk == 0 else rings // 2
        for i in range(n):
            r = 18 + i * (34 + i * 2.2)
            pts = []
            for a in range(0, 360, 6):
                t = math.radians(a)
                wob = 1 + sum(amp * math.sin((k + 2) * t + ph + i * 0.18) for k, (amp, ph) in enumerate(zip(amps, phases)))
                x = cx + math.cos(t) * r * wob * stretch
                y = cy + math.sin(t) * r * wob / stretch
                pts.append((x, y))
            d = "M" + "L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "Z"
            major = " contour__major" if i % 5 == 4 else ""
            out.append(f'<path class="contour__line{major}" d="{d}"/>')
            if labels and pk == 0 and i % 5 == 4:
                lx, ly = pts[rnd.randrange(len(pts))]
                if 20 < lx < W - 60 and 20 < ly < H - 10:
                    alt = base_alt + (n - i) * step_alt
                    out.append(f'<text class="contour__alt" x="{lx:.0f}" y="{ly:.0f}">{alt:,}</text>')
    out.append("</svg>")
    return "".join(out)


def profile_svg(profile, cls="profile"):
    """Altitude profile of a trip: one point per day's overnight altitude, with acclimatisation bands."""
    pts = [p for p in profile if isinstance(p.get("alt"), (int, float))]
    if len(pts) < 2:
        return ""
    W, H, L, R, T, B = 1000, 300, 64, 24, 34, 54
    top = max(p["alt"] for p in pts)
    ymax = max(3000, math.ceil(top / 1000) * 1000 + (500 if top % 1000 > 700 else 0))
    sx = (W - L - R) / (len(pts) - 1)

    def X(i):
        return L + i * sx

    def Y(a):
        return T + (H - T - B) * (1 - a / ymax)

    out = [f'<svg class="{cls}" viewBox="0 0 {W} {H}" role="img" aria-label="Altitude by day, highest {top:,} metres" xmlns="http://www.w3.org/2000/svg">',
           '<defs><linearGradient id="pf-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="currentColor" stop-opacity=".38"/>'
           '<stop offset="1" stop-color="currentColor" stop-opacity="0"/></linearGradient></defs>']
    for a in range(0, ymax + 1, 1000):
        y = Y(a)
        out.append(f'<line class="profile__grid" x1="{L}" y1="{y:.1f}" x2="{W - R}" y2="{y:.1f}"/>'
                   f'<text class="profile__tick" x="{L - 10}" y="{y + 4:.1f}" text-anchor="end">{a:,} m</text>')
    for a, label in ((2500, "Above 2,500 m: go slowly"), (3500, "Above 3,500 m: sleep lower if you can")):
        if a < ymax:
            y = Y(a)
            out.append(f'<line class="profile__band" x1="{L}" y1="{y:.1f}" x2="{W - R}" y2="{y:.1f}"/>'
                       f'<text class="profile__bandlabel" x="{W - R}" y="{y - 6:.1f}" text-anchor="end">{label}</text>')
    line = " ".join(f"{X(i):.1f},{Y(p['alt']):.1f}" for i, p in enumerate(pts))
    area = f"M{X(0):.1f},{Y(0):.1f} L" + " L".join(f"{X(i):.1f},{Y(p['alt']):.1f}" for i, p in enumerate(pts)) + f" L{X(len(pts) - 1):.1f},{Y(0):.1f}Z"
    out.append(f'<path class="profile__area" d="{area}" fill="url(#pf-fill)"/>')
    out.append(f'<polyline class="profile__line" points="{line}"/>')
    every = 1 if len(pts) <= 9 else 2
    for i, p in enumerate(pts):
        x, y = X(i), Y(p["alt"])
        hi = " is-top" if p["alt"] == top else ""
        out.append(f'<g class="profile__pt{hi}"><circle cx="{x:.1f}" cy="{y:.1f}" r="6"/>'
                   f'<title>Day {p.get("day")}: {escape(p.get("name") or "")} {p["alt"]:,} m</title></g>')
        if i % every == 0 or hi:
            out.append(f'<text class="profile__day" x="{x:.1f}" y="{H - B + 22}" text-anchor="middle">Day {p.get("day")}</text>')
            out.append(f'<text class="profile__name" x="{x:.1f}" y="{H - B + 40}" text-anchor="middle">{escape((p.get("name") or "")[:14])}</text>')
        if hi:
            out.append(f'<text class="profile__alt" x="{x:.1f}" y="{y - 14:.1f}" text-anchor="middle">{p["alt"]:,} m</text>')
    out.append("</svg>")
    return "".join(out)


def ladder_y(alt, top=8586, height=100.0):
    """Percent from the bottom for the altimeter rail (log-ish so the low valleys are not squashed)."""
    alt = max(0, min(alt or 0, top))
    return round(height * math.sqrt(alt / top), 2)
