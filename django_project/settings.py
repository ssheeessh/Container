import os
"""
Django settings for django_project project.

Настройки проекта для локального запуска в Visual Studio Code.
"""

from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent


# -------------------------------------------------------------------
# Основные настройки безопасности
# -------------------------------------------------------------------

# Для учебного локального проекта можно оставить такой ключ.
# В реальном проекте SECRET_KEY нельзя хранить прямо в коде.
SECRET_KEY = 'django-insecure-local-development-key'

# Для локальной разработки включаем режим отладки
DEBUG = True

# Хосты, с которых разрешено открывать приложение
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:30080",
]


# -------------------------------------------------------------------
# Подключенные приложения
# -------------------------------------------------------------------

INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Твое приложение из ЛР4
    'tasks.apps.TasksConfig',
]


# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # Защита от CSRF. Оставляем включенной.
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# -------------------------------------------------------------------
# URL-конфигурация проекта
# -------------------------------------------------------------------

ROOT_URLCONF = 'django_project.urls'


# -------------------------------------------------------------------
# Настройки шаблонов HTML
# -------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Если шаблоны лежат внутри tasks/templates/tasks/,
        # то дополнительный общий путь здесь не обязателен.
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


# -------------------------------------------------------------------
# WSGI-приложение
# -------------------------------------------------------------------

WSGI_APPLICATION = 'django_project.wsgi.application'


# -------------------------------------------------------------------
# База данных
# -------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "vmguard_db"),
        "USER": os.environ.get("DB_USER", "vmguard_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "vmguard_pass"),
        "HOST": os.environ.get("DB_HOST", "postgres"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}


# -------------------------------------------------------------------
# Проверка паролей
# -------------------------------------------------------------------

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


# -------------------------------------------------------------------
# Язык и время
# -------------------------------------------------------------------

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# -------------------------------------------------------------------
# Статические файлы
# -------------------------------------------------------------------

STATIC_URL = 'static/'

# Если у тебя есть отдельная папка static, например:
# Container/static/
# можно раскомментировать:
#
# STATICFILES_DIRS = [
#     BASE_DIR / 'static',
# ]


# -------------------------------------------------------------------
# Тип первичного ключа по умолчанию
# -------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

