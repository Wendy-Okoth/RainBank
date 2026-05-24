"""
Django settings for rainbank project.
"""
from decouple import config
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent  # This is 'backend' folder

# Add FRONTEND_DIR to point to your frontend folder
FRONTEND_DIR = BASE_DIR.parent / 'frontend'  # Goes up to RainBank, then to frontend

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']  # Allow all hosts for development

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',  # For API
    'corsheaders',     # For CORS support
    
    # Our apps
    'core',
    'accounts',
    'api',
    'payments',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add this
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.LanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.TranslationContextMiddleware',
]

# Cache settings (if not already present)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'translation-cache',
        'TIMEOUT': 3600,
    }
}

ROOT_URLCONF = 'rainbank.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            FRONTEND_DIR / 'templates',  # Primary: frontend/templates/
            BASE_DIR / 'templates',      # Fallback: backend/templates/ (if exists)
        ],
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

WSGI_APPLICATION = 'rainbank.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'  # Changed to Kenya time
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    FRONTEND_DIR / 'static',  # frontend/static/ for CSS/JS
    BASE_DIR / 'static',      # backend/static/ fallback
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development

# Session settings (for farmer login)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# RainBank Custom Settings
CARBON_PRICE_PER_TON_USD = 10
PAYOUT_PER_ACRE_KES = 2500
DROUGHT_TRIGGER_DAYS = 10
DROUGHT_TRIGGER_PERCENTAGE = 70  # Below 70% of average triggers payout

# Africa's Talking (to be configured later)
AFRICASTALKING_USERNAME = ''
AFRICASTALKING_API_KEY = ''
AFRICASTALKING_SHORTCODE = '*384#'

# M-Pesa (to be configured later)
MPESA_CONSUMER_KEY = ''
MPESA_CONSUMER_SECRET = ''
MPESA_SHORTCODE = ''
MPESA_PASSKEY = ''

# DeepL API Configuration
DEEPL_API_KEY = config('DEEPL_API_KEY', default='')
DEEPL_API_URL = config('DEEPL_API_URL', default='https://api-free.deepl.com/v2/translate')