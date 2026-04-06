import os
from pathlib import Path
from collections.abc import Mapping
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SERVER_KEY")

DEFAULT_ALLOWED_HOSTS = "jakarupora.telco.com.ar,179.0.181.50"


def env_bool(
    name: str,
    default: bool,
    environ: Mapping[str, str] | None = None,
) -> bool:
    env = environ or os.environ
    value = env.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(
    name: str,
    default: str,
    environ: Mapping[str, str] | None = None,
) -> list[str]:
    env = environ or os.environ
    raw_value = env.get(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def build_runtime_settings(
    environ: Mapping[str, str] | None = None,
) -> dict[str, bool | list[str]]:
    return {
        "DEBUG": env_bool("DJANGO_DEBUG", False, environ),
        "ALLOWED_HOSTS": env_list(
            "DJANGO_ALLOWED_HOSTS",
            DEFAULT_ALLOWED_HOSTS,
            environ,
        ),
        "SESSION_COOKIE_SECURE": env_bool(
            "DJANGO_SESSION_COOKIE_SECURE",
            True,
            environ,
        ),
        "CSRF_COOKIE_SECURE": env_bool(
            "DJANGO_CSRF_COOKIE_SECURE",
            True,
            environ,
        ),
    }


def build_database_config(
    base_dir: Path,
    environ: Mapping[str, str] | None = None,
) -> dict[str, dict[str, str | Path]]:
    env = environ or os.environ
    db_engine = env.get("DJANGO_DB_ENGINE", "mysql").strip().lower()

    if db_engine == "sqlite":
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": env.get("DJANGO_DB_NAME", base_dir / "db.sqlite3"),
            }
        }

    return {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env.get("DJANGO_DB_NAME", "mds"),
            "USER": env.get("DJANGO_DB_USER", env.get("DB_USER")),
            "PASSWORD": env.get("DJANGO_DB_PASSWORD", env.get("DB_PASSWORD")),
            "HOST": env.get("DJANGO_DB_HOST", "127.0.0.1"),
            "PORT": env.get("DJANGO_DB_PORT", "3306"),
        }
    }

# SECURITY WARNING: don't run with debug turned on in production!
runtime_settings = build_runtime_settings()

DEBUG = runtime_settings["DEBUG"]

ALLOWED_HOSTS = runtime_settings["ALLOWED_HOSTS"]

SESSION_COOKIE_SECURE = runtime_settings["SESSION_COOKIE_SECURE"]
CSRF_COOKIE_SECURE = runtime_settings["CSRF_COOKIE_SECURE"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'jakaru_pora'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MDS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MDS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = build_database_config(BASE_DIR)


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = "core.User"


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
