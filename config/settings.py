from datetime import timedelta
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = 'django-insecure-&pdpo+5$+u*0wofsa_9p@_er1isjd*5ep&nff=8y*@bc6^#ah2'


DEBUG = True

from dotenv import load_dotenv
load_dotenv()

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS.split(",") if host.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_registration',
    'drf_yasg',
    'accounts',
    'leaves',
    'projects',
    'attendance',
    'timesheet',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
    'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    'RESET_PASSWORD_VERIFICATION_ENABLED': False,
    'REGISTER_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],

}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False") == "True"

csrf_trusted = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [c.strip() for c in csrf_trusted.split(",") if c.strip()]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

SWAGGER_BASE_URL = os.getenv("SWAGGER_BASE_URL", "")

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'LOGIN_URL': None,
    'LOGOUT_URL': None,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Enter token in format: Bearer <your_token>',
        }
    },
}
