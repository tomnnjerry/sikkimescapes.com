# sikkimescapes.com

Django site for Sikkim Escapes: Sikkim-only trips from shared-jeep budget escapes to premium tours. Every page
is rendered from JSON content files; there is no CMS and the database holds only enquiries and newsletter sign-ups.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser        # to read enquiries at /admin/
python manage.py runserver
```

In DEBUG the content catalogue reloads whenever a JSON file changes, so edits show on refresh.

## Layout

| Path | What it is |
| --- | --- |
| `content/<district>/` | One folder per district: `region.json`, `places/`, `journeys/` (packages), `guides/`, `stays.json`, `festivals.json`, `routes.json` |
| `content/SCHEMA.md`, `content/FACTS.md` | The content schema, house writing rules and verified facts. Read both before writing content |
| `content/_places.json` | Binding master list of place slugs per district |
| `content/themes.json`, `content/outlines.json` | Travel themes; map outlines for the self-drawn SVG atlas |
| `content/images.json` | Credited Wikimedia Commons photos, built by `tools/fetch_images.py` |
| `content/journal/` | Journal posts (optional, see `content/JOURNAL_SCHEMA.md`) |
| `escapes/content.py` | Loads all JSON into an in-memory catalogue and links objects together |
| `escapes/views*.py`, `escapes/urls.py` | Pages. Districts live at the top level: `/north-sikkim/lachung/` |
| `templates/escapes/` | Templates; reusable pieces in `partials/` |
| `static/css/milestone.css`, `static/js/milestone.js` | The "Milestone" design system and its behaviour (no JS libraries) |
| `escapes/policies.py` | Policy page drafts. Every `[BRACKETED]` value needs legal review before launch |

## Tools

```bash
python tools/check_region.py north-sikkim --wiki   # validate one district's content (and Wikipedia titles)
python tools/check_journal.py                      # validate journal posts
python tools/fetch_images.py [district ...]        # fetch credited photos into content/images.json (network)
python tools/smoke.py                              # render every URL in the sitemap and report failures
python tools/build_outlines.py                     # rebuild map outlines from Natural Earth
```

## Before launch

- Set the business details in `se/settings.py` (`SITE`): email, phone, WhatsApp number and office address
  (or the `SE_EMAIL`, `SE_PHONE`, `SE_WHATSAPP` environment variables).
- Fill in every `[BRACKETED]` value in `escapes/policies.py` after legal review.
- Production environment: `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY=<random>`, `DJANGO_ALLOWED_HOSTS`, optional `SE_GA4`.
  Run `python manage.py collectstatic`, then set `SE_HASHED_STATIC=1`. HTTPS redirect is on by default when
  DEBUG is off (`SE_SSL_REDIRECT=0` to disable behind a proxy that already redirects); raise `SE_HSTS_SECONDS`
  once HTTPS is confirmed.
- Re-check `content/FACTS.md` against current permit and road rules: they change often.
