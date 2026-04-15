from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default-key-for-dev-only')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Get allowed hosts from environment
allowed_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Add Railway default domain if not present
if 'RAILWAY_ENVIRONMENT' in os.environ and '*.railway.app' not in allowed_hosts:
    allowed_hosts.append('*.railway.app')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    # Local apps
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'panaderia_backend.urls'

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

WSGI_APPLICATION = 'panaderia_backend.wsgi.application'

# Database configuration
# Use DATABASE_URL environment variable if available (Railway provides this)
if all(os.getenv(var) for var in ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('PGDATABASE'),
            'USER': os.getenv('PGUSER'),
            'PASSWORD': os.getenv('PGPASSWORD'),
            'HOST': os.getenv('PGHOST'),
            'PORT': os.getenv('PGPORT', '5432'),
        }
    }
elif DATABASE_URL := os.getenv('DATABASE_URL'):
    # Fallback a DATABASE_URL solo si existe y no tiene placeholders
    # Si contiene {{...}}, ignórala y usa valores por defecto
    if '{{' not in DATABASE_URL:
        DATABASES = {'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)}
    else:
        # Si tiene placeholders, usar valores por defecto (solo desarrollo)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME', 'panaderia_db'),
                'USER': os.getenv('DB_USER', 'postgres'),
                'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', '5432'),
            }
        }
else:
    # Configuración por defecto para desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'panaderia_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
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

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# CORS configuration
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    # Remove empty strings from the list
    CORS_ALLOWED_ORIGINS = [origin for origin in CORS_ALLOWED_ORIGINS if origin]

CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Logging — write everything to stderr so it appears in Railway deploy logs.
# DEBUG level is intentionally used here to surface any initialisation issue.
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['stderr'],
        'level': 'DEBUG',
    },
    'loggers': {
        # Django internals — keep at INFO to avoid drowning out app messages.
        'django': {
            'handlers': ['stderr'],
            'level': 'INFO',
            'propagate': False,
        },
        # Show every SQL query so we can spot a hanging DB call.
        'django.db.backends': {
            'handlers': ['stderr'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Our own WSGI bootstrap logger.
        'panaderia_backend.wsgi': {
            'handlers': ['stderr'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    # Remove empty strings from the list
    CSRF_TRUSTED_ORIGINS = [origin for origin in CSRF_TRUSTED_ORIGINS if origin]
    # Ensure ALLOWED_HOSTS includes Railway domain
    if 'RAILWAY_ENVIRONMENT' in os.environ and '*.railway.app' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('*.railway.app')