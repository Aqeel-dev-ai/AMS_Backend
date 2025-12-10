from datetime import timedelta
from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
import dj_database_url
from dotenv import load_dotenv

# Load .env for local dev; on Render the env vars will come from the system
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================
# ENVIRONMENT
# =========================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # "development" / "production"

# Secret key
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())

# Debug
DEBUG = os.getenv("DEBUG", "False") == "True"

# Allowed hosts
ALLOWED_HOSTS_ENV = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [
    host.strip()
    for host in ALLOWED_HOSTS_ENV.split(",")
    if host.strip()
]

# =========================================
# APPLICATIONS
# =========================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_registration",
    "drf_yasg",
    "accounts",
    "leaves",
    "projects",
    "attendance",
    "timesheet",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be near top
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# =========================================
# DATABASES
# - SQLite for local when DATABASE_URL is not set
# - Use DATABASE_URL (e.g., on Render) when provided
# =========================================

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,        # Required by Render
            conn_health_checks=True, # Django 4.1+
        )
    }
elif DB_NAME:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }
else:
    # Default to SQLite (good for local dev)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =========================================
# PASSWORD VALIDATION
# =========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =========================================
# INTERNATIONALIZATION
# =========================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =========================================
# STATIC & MEDIA
# =========================================

STATIC_URL = "/static/"

# Media files (uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

# =========================================
# AUTH / DRF / JWT
# =========================================

REST_REGISTRATION = {
    "REGISTER_VERIFICATION_ENABLED": False,
    "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
    "RESET_PASSWORD_VERIFICATION_ENABLED": False,
    "REGISTER_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}

# =========================================
# CORS / CSRF
# =========================================

# Global switch: allow everything (useful only in dev)
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False") == "True"

# If CORS_ALLOW_ALL_ORIGINS is False, we use this whitelist
cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in cors_origins_env.split(",")
    if o.strip()
]

csrf_trusted_env = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    c.strip()
    for c in csrf_trusted_env.split(",")
    if c.strip()
]

# If you're using cookies/session auth from a different domain:
CORS_ALLOW_CREDENTIALS = True

# =========================================
# SECURITY (production hardening)
# =========================================

if ENVIRONMENT == "production":
    # Force HTTPS in production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Optionally:
    # CSRF_COOKIE_SAMESITE = "None"
    # SESSION_COOKIE_SAMESITE = "None"
else:
    # Local dev defaults
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# =========================================
# SWAGGER
# =========================================

SWAGGER_BASE_URL = os.getenv("SWAGGER_BASE_URL", "")

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "LOGIN_URL": None,
    "LOGOUT_URL": None,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter token in format: Bearer <your_token>",
        }
    },
}


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"        # ← new folder for collected files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =========================================
# EMAIL CONFIGURATION
# =========================================

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", 
    "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# For development, you can use console backend to print emails to console
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"