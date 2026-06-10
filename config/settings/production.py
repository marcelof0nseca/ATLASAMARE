import os

from .base import *  # noqa: F403


DEBUG = False

render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME", "")
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)  # noqa: F405
    CSRF_TRUSTED_ORIGINS = [f"https://{render_hostname}"]
else:
    CSRF_TRUSTED_ORIGINS = []

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
