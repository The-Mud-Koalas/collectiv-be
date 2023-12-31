"""
Django settings for communalspace project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from .credentials_setup import firebase_admin, google_storage
from datetime import timedelta
from dotenv import load_dotenv
from firebase_admin import auth, credentials, initialize_app
from pathlib import Path
import dj_database_url
import os

load_dotenv()

firebase_admin.setup_firebase_admin_credentials()
google_storage.setup_google_storage_credentials()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET']  # NOSONAR

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('ENVIRONMENT', 'DEVELOPMENT') == 'DEVELOPMENT'

ALLOWED_HOSTS = ['*']
CORS_ALLOW_HEADERS = ['*']
CORS_ALLOWED_ORIGINS = [
    'https://collectiv-fe-display.vercel.app',
    'https://collectiv-fe-web.vercel.app',
    'https://mud-koalas-communal-space-stg-oxybezqe2a-ts.a.run.app',
    'https://mud-koalas-communal-space-76mcmzlezq-ts.a.run.app',
]

if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        *CORS_ALLOWED_ORIGINS,
        'http://localhost:8000',
        'http://localhost:3000'
    ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'polymorphic',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_apscheduler',

    'analytics',
    'event',
    'participation',
    'report',
    'review',
    'reward',
    'space',
    'users',
    'forums',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'communalspace.middleware.CorsOriginPresenceMiddleware',
]

ROOT_URLCONF = 'communalspace.urls'

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

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'communalspace.exception_config.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 2,
}

WSGI_APPLICATION = 'communalspace.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'

# Firebase Admin Configuration
FIREBASE_CREDENTIAL = credentials.Certificate(r'firebase-credentials.json')
FIREBASE_APP = initialize_app(credential=FIREBASE_CREDENTIAL)

# Google Bucket Storage
GOOGLE_BUCKET_BASE_DIRECTORY = 'event-images'
GOOGLE_STORAGE_BUCKET_NAME = 'artifacts.mud-koalas-communal-space.appspot.com'

# Pagination Settings
DEFAULT_PAGE_LIMIT = 10

# Geofencing setting (in KM)
AREA_RADIUS = 0.1
AREA_BUFFER_RADIUS = 0.3

# Reward Settings
MINIMUM_SECONDS_FOR_REWARD_ELIGIBILITY = 0
POINTS_PER_ATTENDANCE = 1

# Settings for Automatic Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'smtp.gmail.com')

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25  # Seconds

# AI Model Settings
HUGGING_FACE_ACCESS_TOKEN = os.getenv("HUGGING_FACE_ACCESS_TOKEN")
SENTIMENT_ANALYSIS_ENDPOINT = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
TOKEN_CLASSIFICATION_ENDPOINT = "https://api-inference.huggingface.co/models/xlm-roberta-large-finetuned-conll03-english"
