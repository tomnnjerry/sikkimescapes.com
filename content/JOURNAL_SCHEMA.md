# Journal posts: schema

Journal posts live in `content/journal/<slug>.json`, one file per post, and appear at `/journal/<slug>/`.
All the house rules in `content/SCHEMA.md` (voice, banned words, no invented facts, "check current status before
you travel") and the facts in `content/FACTS.md` apply. Validate with `python tools/check_journal.py`.

```json
{
  "slug": "same-as-filename",
  "title": "≤ 60 chars, no full stop",
  "category": "Planning | Money | Seasons | Stories | Food | Permits | Road news",
  "date": "2026-10-04",
  "regions": ["north-sikkim"],
  "meta_description": "≤ 158 chars",
  "summary": "40–60 words, answer first",
  "wiki": "", "image_query": "3–6 words that find a real Commons photo",
  "key_takeaways": ["…", "…", "…", "…"],
  "sections": [
    {"heading": "≤ 50 chars", "paras": ["…"], "list": ["optional"],
     "table": {"head": ["…"], "rows": [["…"]]},
     "links": [{"type": "journey | place | stay | guide | festival", "slug": "existing-slug"}]}
  ],
  "related_journeys": ["journey-slug"],
  "related_places": ["place-slug"],
  "cta": "one sentence inviting the reader to ask for a priced plan",
  "faqs": [{"q": "…", "a": "…"}]
}
```

Rules checked by the validator: exactly 4 `key_takeaways`, exactly 5 `faqs`, at least one section with a `table`,
at least 1,050 words of body across sections, `regions` must be district slugs, and every linked slug must exist.
The category becomes a topic page at `/journal/topic/<category-slug>/`.
