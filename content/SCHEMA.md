# Sikkim Escapes: content schema and house rules

Sikkim Escapes (sikkimescapes.com) is a Sikkim-only travel company based in Gangtok that sells honest,
affordable trips as well as comfortable and premium ones. Byline on everything: "Sikkim Escapes Desk".
Voice: a local friend who knows the roads, the prices and the stories. First person plural ("we"). Warm,
exact, never salesy. Audience: Indian families, couples, groups of friends and first-time Himalaya travellers
on a budget, plus some international travellers (who face permit limits, say so).

The site's promise has three parts, and every page should serve them:
1. **Rooted stories**: the Lepcha, Bhutia, Limbu, Nepali, Sherpa, Rai, Tamang and Newar histories, names and
   customs behind each place, told with a checkable source. This is what makes us different from every other
   Sikkim site. Look for the specific and the little known: what a place-name means in Lepcha, who built the
   bridge, which monastery's mask dance falls on which day of the Tibetan calendar, what the cardamom farmer
   earns, why Dzongu is reserved. Never invent.
2. **Honest prices**: real indicative costs (shared jeep fares, cab hire, homestay rates, permit fees) so a
   reader can budget before talking to us. Always "indicative" and "check current status before you travel".
3. **Altitude**: Sikkim rises from about 280 m in the Rangeet/Teesta valleys to 8,586 m at Kangchenjunga in under
   100 km. Every place has an accurate `altitude_m`, and we talk plainly about acclimatisation.

All content is JSON, UTF-8, under `content/<district-slug>/`. The JSON must parse (no comments, no trailing
commas). Slugs are lowercase-hyphenated ASCII and unique within their type across the WHOLE site (prefix with the
place or district if needed). Read `content/FACTS.md` (verified facts: permits, road status, fees) and obey it.
Read `content/_places.json`: it is the binding master list of place slugs for all six districts.

## Districts (slugs)
east-sikkim (Gangtok district), north-sikkim (Mangan district), west-sikkim (Gyalshing district),
south-sikkim (Namchi district), pakyong (Pakyong district, includes the Old Silk Route), soreng (Soreng district).
Sikkim reorganised from 4 to 6 districts in December 2021: Pakyong was carved from East Sikkim and Soreng from West
Sikkim, and the districts were renamed Gangtok, Mangan, Gyalshing and Namchi. Travellers still search "North Sikkim"
etc., so use both names where useful ("Mangan district (North Sikkim)").

## Writing rules (strict)

- Headings and titles: no full stop at the end; short, one line on desktop (≤ 60 characters).
- Plain and specific: numbers over adjectives (km, hours, metres, ₹, months, °C).
- BANNED words/phrases: nestled, breathtaking, hidden gem, paradise, tapestry, embark, delve, unleash, vibrant,
  bustling, mesmerizing, stunning, magical, heaven on earth, a feast for the eyes, something for everyone,
  whether you're, look no further, ultimate guide, in this blog, in conclusion, unforgettable, world-class,
  seamless, curated, elevate, immerse, timeless, jewel, boasts, abode of peace, land of mystic, Switzerland of,
  offbeat gem, must-visit, bucket list.
- No emoji. No exclamation marks. Do not use "Shangri-La".
- Facts that change (permits, road openings, closures, fees, fares, festival dates): state the rule as you
  understand it and add "check current status before you travel".
- Never invent reviews, awards, statistics, star ratings, founders, staff names, client counts, "since 19xx",
  legends or folk tales. A story must name its source tradition and a checkable source (book, Wikipedia article,
  government or monastery page, museum). Local tradition without a written source: say "as told locally" and keep
  it short. If unsure of a fact, leave it out or soften it and list it in your hand-off report.
- Write respectfully about communities: no "exotic", "primitive", "untouched", no photos of people as scenery.
- Prices: indicative "from" INR per person, twin sharing, rounded to the nearest 500. Realistic for 2026:
  shared jeep Gangtok–Lachung around ₹500–800 per seat; reserved small car (Alto/WagonR class) Gangtok sightseeing
  around ₹3,000–4,000 a day; North Sikkim 2N/3D package from Gangtok around ₹6,500–9,000 pp budget; budget hotel
  rooms ₹1,500–3,000; homestays ₹1,200–2,500 pp with meals; premium hotels ₹12,000–30,000 a room. Use your best
  judgement and keep everything plausible and consistent with FACTS.md.
- Hotels and homestays: REAL, currently operating properties only. Do not invent amenities, room counts, awards
  or exact prices (use a band). If unsure a property operates, leave it out. A homestay cluster may be listed as a
  village (kind "homestay village", e.g. `dzongu-lepcha-homestays`) without naming a family.
- Distances and drive times must be realistic for Sikkim's roads (20–25 km/h average in the hills):
  "≈ 125 km · 5 h".
- `best_months` is ALWAYS an array of 12 integers, Jan..Dec: 2 = best, 1 = good, 0 = avoid/closed.
- `wiki` = the EXACT title of an existing English Wikipedia article about that thing (used to fetch photos with
  credits). Use "" if none exists. Do not guess: check if you can.
- `image_query` = 3–6 words that would find a real photo of exactly that subject on Wikimedia Commons
  (e.g. "Rumtek Monastery courtyard Sikkim", "Yumthang valley rhododendron").
- FAQs: real questions travellers search for; answers 40–90 words, answer first, specific.
- `altitude_m`: accurate integer metres.

## THEMES (use these slugs only)
monasteries, lakes-and-passes, snow-and-winter, flowers-and-forests, village-homestays, honeymoons,
family-holidays, treks-and-walks, food-and-tea, festivals, birds-and-wildlife, photography, crafts-and-culture,
offbeat-sikkim

## TIERS (journeys and stays)
budget (shared jeeps or a small shared car, clean budget hotels and homestays), value (private small car, good
3-star hotels and better homestays), comfort (private SUV, the best mid-range hotels and resorts), premium (top
hotels such as Mayfair, Taj Guras Kutir, Elgin, The Chumbi Residency class, private everything).

## EXPERIENCE KINDS
culture, nature, wildlife, food, adventure, spiritual, craft, village, wellness

## Files to write for each district `<d>`

### 1. `content/<d>/region.json`
```json
{
  "slug": "north-sikkim", "name": "North Sikkim", "official": "Mangan district", "hq": "Mangan",
  "tagline": "≤ 8 words",
  "meta_description": "≤ 158 chars",
  "summary": "40–60 word answer-first summary",
  "intro": ["para (60–110 words)", "para", "para", "para"],
  "story": {"title": "≤ 60 chars", "text": "180–260 words: one rooted story of this district", "source": "checkable source"},
  "little_known": [{"fact": "25–50 words, specific and checkable", "source": "short source name"}],   // exactly 5
  "facts": [["Best months", "…"], ["Headquarters", "…"], ["Nearest airport", "Bagdogra (IXB) ≈ … km"], ["Nearest railhead", "NJP ≈ … km"], ["Altitude range", "… m – … m"], ["Languages", "…"], ["Permits", "…"]],
  "best_months": [1,1,2,2,2,0,0,0,1,2,2,1],
  "highlights": [{"title": "…", "text": "35–60 words"}],          // exactly 6
  "getting_there": "90–150 words",
  "permits": "60–120 words, or ''",
  "money": "80–130 words: what a trip here really costs on a budget, mid and premium level",
  "wiki": "Mangan district",
  "lat": 27.6, "lng": 88.6,
  "months": [                                                      // exactly 12, Jan..Dec
    {"month": "January", "rating": 1, "weather": "Lachung −5 to 8 °C, snow likely", "summary": "60–100 words",
     "go": ["place-slug", "place-slug", "place-slug"], "events": ["festival-slug"], "tip": "one sentence"}
  ],
  "faqs": [{"q": "…", "a": "…"}]                                    // exactly 9
}
```

### 2. `content/<d>/places/<place-slug>.json` (one file per place)
```json
{
  "slug": "lachung", "name": "Lachung", "region": "north-sikkim",
  "kind": "town | village | valley | lake | pass | monastery | viewpoint | sanctuary | waterfall | heritage site | tea garden | trek | pilgrimage site | garden",
  "wiki": "Lachung", "image_query": "Lachung village Sikkim",
  "lat": 27.69, "lng": 88.74, "altitude_m": 2700,
  "local_name": {"name": "…", "language": "Lepcha | Bhutia | Nepali | Limbu | Tibetan", "meaning": "…", "source": "…"},   // or null if not documented
  "tagline": "≤ 70 chars",
  "meta_description": "≤ 158 chars",
  "summary": "40–60 word answer-first summary",
  "intro": ["para 70–120 words", "para", "para"],
  "story": {"title": "≤ 60 chars", "text": "120–200 words", "source": "checkable source"},
  "little_known": [{"fact": "20–45 words", "source": "short source name"}],   // exactly 3
  "facts": [["Best months", "…"], ["Nights we suggest", "1–2"], ["From Gangtok", "≈ 118 km · 5–6 h"], ["Altitude", "2,700 m"], ["Known for", "…"], ["Permit", "… or 'Not needed'"]],
  "best_months": [1,1,2,2,2,1,0,0,1,2,2,1],
  "nights": "1–2",
  "highlights": [{"title": "…", "text": "35–60 words"}],          // 5–6
  "how_to_reach": [{"mode": "Shared jeep", "text": "…"}, {"mode": "Private car", "text": "…"}, {"mode": "From Bagdogra / NJP", "text": "…"}],
  "costs": [["Shared jeep from Gangtok", "≈ ₹600–800 a seat"], ["Budget room", "≈ ₹1,500–2,500"], ["Permit", "…"], ["Meal (thali)", "≈ ₹150–250"]],  // 4–6 rows, indicative
  "where_to_stay": "70–120 words naming areas and real properties across budgets",
  "stays": ["stay-slug"],                                         // slugs from your stays.json in this place, may be []
  "tips": ["one sentence", "…"],                                   // 5
  "themes": ["lakes-and-passes", "snow-and-winter"],               // 2–4 from THEMES
  "nearby": ["place-slug"],                                        // 2–4 places from _places.json or your district
  "experiences": [                                                 // exactly 4
    {"slug": "lachung-apple-orchard-walk", "title": "≤ 55 chars", "kind": "culture | nature | wildlife | food | adventure | spiritual | craft | village | wellness",
     "duration": "2 hours", "best_time": "…", "cost": "≈ ₹… per person or 'Free'",
     "image_query": "…", "wiki": "",
     "summary": "35–55 words", "body": ["para 70–120 words", "para", "para"],
     "good_for": ["couples", "families", "first-timers", "photographers", "solo", "seniors", "budget"],
     "faqs": [{"q": "…", "a": "…"}]}                                // exactly 3
  ],
  "faqs": [{"q": "…", "a": "…"}]                                    // exactly 9
}
```

### 3. `content/<d>/journeys/<journey-slug>.json` (packages: our commercial core)
```json
{
  "slug": "gangtok-lachung-pelling-budget-6n", "title": "≤ 50 chars", "region": "north-sikkim",
  "tier": "budget | value | comfort | premium",
  "nights": 6, "themes": ["lakes-and-passes", "family-holidays"],
  "stops": [{"place": "gangtok", "nights": 2}, {"place": "lachung", "nights": 2}],   // nights sum = nights; any slug from _places.json
  "start": "Bagdogra Airport (IXB) or NJP station", "end": "Bagdogra Airport (IXB) or NJP station",
  "price_from_inr": 16500,
  "price_basis": "per person, twin sharing, 2 people, small private car, budget hotels with breakfast",
  "price_breakdown": [["Stays, 6 nights", 7500], ["Car and driver", 6500], ["Permits and fees", 500], ["Our planning fee", 2000]],  // sums to price_from_inr (±5%)
  "best_months": [1,1,2,2,2,0,0,0,1,2,2,1],
  "pace": "Easy | Balanced | Active", "max_altitude_m": 4310,
  "meta_description": "≤ 158 chars including 'N nights' and the price",
  "summary": "40–60 words", "intro": ["para 70–120 words", "para"],
  "highlights": ["…"],                                                          // 5
  "days": [{"day": 1, "title": "≤ 45 chars", "place": "gangtok", "overnight": "Gangtok", "alt_m": 1650, "drive": "≈ 125 km · 4.5 h or ''", "text": "70–130 words", "meals": "Dinner"}],  // days = nights + 1; last day overnight "" and alt_m of where it ends
  "stays": ["stay-slug"],                                                      // stays from your own stays.json only, may be []
  "includes": ["…"], "excludes": ["…"],
  "good_to_know": ["…"],
  "upgrade": "one sentence: what the next tier up changes and roughly costs",
  "faqs": [{"q": "…", "a": "…"}]                                                // exactly 9
}
```
Price guide (pp twin sharing, 2026, indicative): budget 3N ≈ ₹7,000–11,000, 5–6N ≈ ₹13,000–20,000;
value 5–6N ≈ ₹22,000–32,000; comfort 6–7N ≈ ₹38,000–60,000; premium 6–7N ≈ ₹80,000–1,60,000.
Journeys must be realistic: North Sikkim needs a minimum 2-night stay and permits; Nathu La is Indians only; no
same-day Gurudongmar from Gangtok.

### 4. `content/<d>/stays.json` — array
```json
[{"slug": "the-fortune-resort-lachung", "name": "…", "place": "lachung", "tier": "budget | value | comfort | premium",
  "kind": "hotel | resort | homestay | homestay village | boutique hotel | heritage bungalow | farmstay | camp",
  "price_band": "≈ ₹2,500–4,000 a room a night (indicative)",
  "wiki": "", "image_query": "…",
  "summary": "35–55 words", "body": ["para 70–110 words", "para"],
  "why": ["one line", "one line", "one line"], "best_for": ["couples", "…"],
  "website": "official URL only if certain, else ''",
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 3
```

### 5. `content/<d>/guides/<guide-slug>.json`
```json
{"slug": "north-sikkim-permits-guide", "title": "≤ 60 chars", "region": "north-sikkim",
 "category": "planning | seasons | stays | culture | food | money | practical | journeys | stories",
 "meta_description": "≤ 158 chars", "summary": "40–60 words answer-first",
 "sections": [{"heading": "≤ 50 chars", "paras": ["…"], "list": ["optional"], "table": {"head": ["…"], "rows": [["…"]]}}],
 "related_places": ["place-slug"],
 "faqs": [{"q": "…", "a": "…"}]}                                                 // exactly 9
```
Guides: 1,100–1,600 words of body across 5–8 sections; use a table in at least one section. Every district needs
at least one `money` guide (real costs) and one `stories` guide (rooted history and people).

### 6. `content/<d>/festivals.json` — array
```json
[{"slug": "pang-lhabsol", "name": "Pang Lhabsol", "place": "gangtok", "wiki": "Pang Lhabsol",
  "image_query": "…", "when": "Aug–Sep, 15th day of the 7th Tibetan month (lunar)", "month_nums": [8, 9],
  "community": "Bhutia and Lepcha",
  "summary": "35–55 words", "body": ["para 70–110 words", "para", "para"], "tips": ["…", "…", "…"],
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 4
```

### 7. `content/<d>/routes.json` — array: getting between two places
```json
[{"slug": "gangtok-to-lachung", "from": "gangtok", "to": "lachung", "distance_km": 118,
  "summary": "35–55 words",
  "options": [{"mode": "Shared jeep", "time": "5–6 h", "cost": "≈ ₹…", "text": "50–90 words"}, {"mode": "Private car", "time": "…", "cost": "≈ ₹…", "text": "…"}],
  "stops_on_way": ["…"], "tip": "one sentence",
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 4
```
`from` and `to` must be place slugs (yours or from _places.json).

## Cross-references
Places (`go`, `nearby`, journey `stops`, routes, `related_places`) may use any slug in `_places.json` plus places
in your own district. Stays and festivals referenced must exist in your own district's files.

## Validate
`python tools/check_region.py <district> --wiki` must print OK before you report. Warnings about banned words must
be fixed too.
