import os
from pathlib import Path
import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# .env faqat local devda yuklanadi, productionда Railway env vars ishlatadi
dotenv.load_dotenv(BASE_DIR / '.env')

# ── SECURITY ──────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'edunify.online',
    'www.edunify.online',
    '.railway.app',       # Railway subdomain
    '.onrender.com',      # Render subdomain (backup)
]

# ── APPS ──────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Uchinchi tomon
    'crispy_forms',
    'crispy_bootstrap5',
    'social_django',           # Google OAuth

    # Loyiha
    'users',
    'courses',
    'quiz',
    'ai_assistant',
]

# ── MIDDLEWARE ────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # Static fayllar uchun
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',  # Google OAuth
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',   # Google OAuth
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── DATABASE ──────────────────────────────────────
# Railway PostgreSQL → DATABASE_URL env var avtomatik beriladi
DATABASE_URL = os.getenv('DATABASE_URL', '')

if DATABASE_URL:
    # Production: PostgreSQL (Railway)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
elif os.getenv('USE_SQLITE', 'True').lower() in ('true', '1', 'yes'):
    # Local dev: SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Local dev: MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'edutj_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }

# ── PASSWORD VALIDATORS ───────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── I18N ─────────────────────────────────────────
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# ── STATIC FILES ─────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'          # collectstatic uchun

# WhiteNoise — production static xizmat qiluvchi
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── MEDIA FILES ───────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── OTHER ─────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ── GEMINI AI ─────────────────────────────────────
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# ── GOOGLE OAUTH ──────────────────────────────────────────
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY    = os.getenv('GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_OAUTH2_SECRET', '')

# Redirect URI'ni qo'lda belgilash (redirect_uri_mismatch xatosini tuzatadi)
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = os.getenv(
    'GOOGLE_OAUTH2_REDIRECT_URI',
    'https://www.edunify.online/auth/complete/google-oauth2/'
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SOCIAL_AUTH_LOGIN_REDIRECT_URL    = '/users/dashboard/'
SOCIAL_AUTH_LOGIN_ERROR_URL       = '/users/login/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/users/dashboard/'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'users.pipeline.set_student_role',    # Yangi user = student
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# ── PRODUCTION SECURITY (DEBUG=False da ishlaydi) ─
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Google OAuth productionда HTTPS redirect ishlatadi
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

# ── CSRF TRUSTED ORIGINS ──────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'https://edunify.online',
    'https://www.edunify.online',
    'https://*.onrender.com',
    'https://*.railway.app',
]
