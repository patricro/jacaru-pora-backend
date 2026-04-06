from pathlib import Path
from unittest.mock import patch
from django.test import SimpleTestCase
from MDS.settings import build_database_config, build_runtime_settings


class SettingsCompatibilityTests(SimpleTestCase):

    def test_runtime_settings_use_secure_defaults(self):
        runtime_settings = build_runtime_settings({})

        self.assertFalse(runtime_settings["DEBUG"])
        self.assertEqual(
            runtime_settings["ALLOWED_HOSTS"],
            ["jakarupora.telco.com.ar", "179.0.181.50"],
        )
        self.assertTrue(runtime_settings["SESSION_COOKIE_SECURE"])
        self.assertTrue(runtime_settings["CSRF_COOKIE_SECURE"])

    def test_runtime_settings_allow_env_overrides(self):
        runtime_settings = build_runtime_settings(
            {
                "DJANGO_DEBUG": "true",
                "DJANGO_ALLOWED_HOSTS": "api.example.com, localhost",
                "DJANGO_SESSION_COOKIE_SECURE": "false",
                "DJANGO_CSRF_COOKIE_SECURE": "0",
            }
        )

        self.assertTrue(runtime_settings["DEBUG"])
        self.assertEqual(
            runtime_settings["ALLOWED_HOSTS"],
            ["api.example.com", "localhost"],
        )
        self.assertFalse(runtime_settings["SESSION_COOKIE_SECURE"])
        self.assertFalse(runtime_settings["CSRF_COOKIE_SECURE"])

    def test_runtime_settings_keep_explicit_empty_mapping_isolated_from_process_env(self):
        with patch.dict(
            "os.environ",
            {
                "DJANGO_DEBUG": "true",
                "DJANGO_ALLOWED_HOSTS": "ci.example.com",
                "DJANGO_SESSION_COOKIE_SECURE": "false",
                "DJANGO_CSRF_COOKIE_SECURE": "false",
            },
            clear=True,
        ):
            runtime_settings = build_runtime_settings({})

        self.assertFalse(runtime_settings["DEBUG"])
        self.assertEqual(
            runtime_settings["ALLOWED_HOSTS"],
            ["jakarupora.telco.com.ar", "179.0.181.50"],
        )
        self.assertTrue(runtime_settings["SESSION_COOKIE_SECURE"])
        self.assertTrue(runtime_settings["CSRF_COOKIE_SECURE"])

    def test_database_config_uses_legacy_mysql_env_by_default(self):
        databases = build_database_config(
            Path("/tmp/jacaru"),
            {
                "DB_USER": "legacy-user",
                "DB_PASSWORD": "legacy-pass",
            },
        )

        self.assertEqual(databases["default"]["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(databases["default"]["NAME"], "mds")
        self.assertEqual(databases["default"]["USER"], "legacy-user")
        self.assertEqual(databases["default"]["PASSWORD"], "legacy-pass")
        self.assertEqual(databases["default"]["HOST"], "127.0.0.1")
        self.assertEqual(databases["default"]["PORT"], "3306")

    def test_database_config_prefers_django_mysql_overrides(self):
        databases = build_database_config(
            Path("/tmp/jacaru"),
            {
                "DB_USER": "legacy-user",
                "DB_PASSWORD": "legacy-pass",
                "DJANGO_DB_NAME": "custom-db",
                "DJANGO_DB_HOST": "db.internal",
                "DJANGO_DB_PORT": "3307",
                "DJANGO_DB_USER": "django-user",
                "DJANGO_DB_PASSWORD": "django-pass",
            },
        )

        self.assertEqual(databases["default"]["NAME"], "custom-db")
        self.assertEqual(databases["default"]["HOST"], "db.internal")
        self.assertEqual(databases["default"]["PORT"], "3307")
        self.assertEqual(databases["default"]["USER"], "django-user")
        self.assertEqual(databases["default"]["PASSWORD"], "django-pass")

    def test_database_config_supports_sqlite(self):
        databases = build_database_config(
            Path("/tmp/jacaru"),
            {
                "DJANGO_DB_ENGINE": "sqlite",
                "DJANGO_DB_NAME": "/tmp/jacaru/dev.sqlite3",
            },
        )

        self.assertEqual(databases["default"]["ENGINE"], "django.db.backends.sqlite3")
        self.assertEqual(databases["default"]["NAME"], "/tmp/jacaru/dev.sqlite3")

    def test_database_config_keeps_explicit_empty_mapping_isolated_from_process_env(self):
        with patch.dict(
            "os.environ",
            {
                "DJANGO_DB_ENGINE": "sqlite",
                "DJANGO_DB_NAME": "/tmp/ci.sqlite3",
                "DJANGO_DB_USER": "ci-user",
            },
            clear=True,
        ):
            databases = build_database_config(Path("/tmp/jacaru"), {})

        self.assertEqual(databases["default"]["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(databases["default"]["NAME"], "mds")
        self.assertIsNone(databases["default"]["USER"])
        self.assertIsNone(databases["default"]["PASSWORD"])
        self.assertEqual(databases["default"]["HOST"], "127.0.0.1")
        self.assertEqual(databases["default"]["PORT"], "3306")
