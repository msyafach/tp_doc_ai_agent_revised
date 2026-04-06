from .settings import *
from pathlib import Path

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Override TP_APP_DIR to point to mock tp_app for testing
TP_APP_DIR = str(Path(__file__).resolve().parent.parent.parent / "tests" / "mock_tp_app")
