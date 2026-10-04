"""Django settings for sikkimescapes.com."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,sikkimescapes.com,www.sikkimescapes.com").split(",")
CSRF_TRUSTED_ORIGINS = ["https://sikkimescapes.com", "https://www.sikkimescapes.com"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "escapes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

try:  # optional: serves /static/ efficiently in production
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
except ImportError:
    pass

ROOT_URLCONF = "se.urls"
WSGI_APPLICATION = "se.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "escapes.context.site",
    ]},
}]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = False
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CONTENT_DIR = BASE_DIR / "content"

# Business details. Fill these before launch; placeholders render as-is.
SITE = {
    "name": "Sikkim Escapes",
    "url": "https://sikkimescapes.com",
    "email": os.environ.get("SE_EMAIL", "[YOUR EMAIL]"),
    "phone": os.environ.get("SE_PHONE", "[YOUR PHONE]"),
    "whatsapp": os.environ.get("SE_WHATSAPP", ""),  # digits with country code, e.g. 919800000000
    "address": "[YOUR OFFICE ADDRESS]",
    "byline": "Sikkim Escapes Desk",
}

# Optional Google Analytics 4 measurement ID (e.g. G-XXXXXXX). Leave empty to load no analytics.
GA4_ID = os.environ.get("SE_GA4", "")

# Production: hashed file names so every deploy busts browser caches.
# Set SE_HASHED_STATIC=1 on the server AFTER `python manage.py collectstatic`.
if os.environ.get("SE_HASHED_STATIC") == "1":
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
                        if "whitenoise.middleware.WhiteNoiseMiddleware" in MIDDLEWARE
                        else "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
    }

# Production hardening: on when DEBUG is off (set DJANGO_DEBUG=0 on the server).
if not DEBUG:
    if SECRET_KEY.startswith("dev-only"):
        raise RuntimeError("Set DJANGO_SECRET_KEY before running with DJANGO_DEBUG=0")
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.environ.get("SE_SSL_REDIRECT", "1") == "1"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SE_HSTS_SECONDS", "0"))  # raise to 31536000 once HTTPS is confirmed
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

LOGGING = {
    "version": 1, "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
