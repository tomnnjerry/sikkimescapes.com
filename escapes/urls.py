from django.urls import path, register_converter

from . import views, views_more, views_shop
from .content import REGION_ORDER


class DistrictConverter:
    regex = "|".join(REGION_ORDER)

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(DistrictConverter, "district")

urlpatterns = [
    path("", views.home, name="home"),
    path("districts/", views.lands, name="lands"),
    # packages (journeys) and the affordable section
    path("packages/", views.journeys, name="journeys"),
    path("packages/tier/<slug:tier>/", views_shop.tier, name="tier"),
    path("packages/<int:n>-nights/", views_shop.nights, name="nights"),
    path("packages/<slug:slug>/", views.journey, name="journey"),
    path("affordable/", views_shop.affordable, name="affordable"),
    path("affordable/<slug:band>/", views_shop.band, name="band"),
    path("stays/", views.stays, name="stays"),
    path("stays/homestays/", views_shop.homestays, name="homestays"),
    path("stays/<slug:slug>/", views.stay, name="stay"),
    path("experiences/", views.experiences, name="experiences"),
    path("experiences/<slug:kind>/", views.experience_kind, name="experience_kind"),
    path("guides/", views.guides, name="guides"),
    path("guides/<slug:slug>/", views.guide, name="guide"),
    path("festivals/", views.festivals, name="festivals"),
    path("festivals/<slug:slug>/", views.festival, name="festival"),
    path("routes/", views.routes, name="routes"),
    path("routes/<slug:slug>/", views.route, name="route"),
    path("themes/", views.themes, name="themes"),
    path("themes/<slug:slug>/", views.theme, name="theme"),
    path("seasons/", views.seasons, name="seasons"),
    path("seasons/<slug:month>/", views_shop.sikkim_month, name="sikkim_month"),
    path("stories/", views_shop.stories, name="stories"),
    path("altitude/", views_shop.altitude, name="altitude"),
    path("tools/", views.tools, name="tools"),
    path("tools/season-finder/", views.tool_season, name="tool_season"),
    path("tools/trip-cost/", views.tool_budget, name="tool_budget"),
    path("tools/permits/", views.tool_permits, name="tool_permits"),
    path("tools/altitude-check/", views_shop.tool_altitude, name="tool_altitude"),
    path("plan/", views.plan, name="plan"),
    path("plan/thank-you/", views.plan_thanks, name="plan_thanks"),
    path("about/", views.static_page, {"page": "about"}, name="about"),
    path("journal/", views_more.journal, name="journal"),
    path("journal/topic/<slug:cat>/", views_more.journal, name="journal_cat"),
    path("journal/<slug:slug>/", views_more.post, name="post"),
    path("policies/", views_more.policies, name="policies"),
    path("policies/<slug:slug>/", views_more.policy, name="policy"),
    path("contact/", views_more.contact, name="contact"),
    path("how-we-work/", views_more.how_we_work, name="how_we_work"),
    path("subscribe/", views_more.subscribe, name="subscribe"),
    path("search.json", views_more.search_index, name="search_index"),
    path("faq/", views.faq, name="faq"),
    path("photo-credits/", views.photo_credits, name="photo_credits"),
    path("sitemap/", views.html_sitemap, name="html_sitemap"),
    path("robots.txt", views.robots, name="robots"),
    path("llms.txt", views.llms, name="llms"),
    # districts live at the top level: /north-sikkim/lachung/
    path("<district:region>/", views.region, name="region"),
    path("<district:region>/in/<slug:month>/", views.region_month, name="region_month"),
    path("<district:region>/themes/<slug:theme>/", views.region_theme, name="region_theme"),
    path("<district:region>/experiences/<slug:kind>/", views.region_kind, name="region_kind"),
    path("<district:region>/budget/", views_shop.region_budget, name="region_budget"),
    path("<district:region>/<slug:place>/", views.place, name="place"),
    path("<district:region>/<slug:place>/<slug:exp>/", views.experience, name="experience"),
]
