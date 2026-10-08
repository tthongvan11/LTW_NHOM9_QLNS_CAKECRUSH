from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.manager = User.objects.create_user(username="manager", password="Manager-Test-938!", role="MANAGER")
        cls.staff = User.objects.create_user(username="staff", password="Staff-Test-938!", role="STAFF")

    def test_login_redirect_uses_actual_account_role(self):
        for username, password, expected in [("manager", "Manager-Test-938!", "employees:employee_list"), ("staff", "Staff-Test-938!", "employees:my_profile")]:
            client = Client()
            response = client.post(reverse("accounts:login"), {"username": username, "password": password, "next": "https://example.invalid/redirect"})
            self.assertRedirects(response, reverse(expected))

    def test_wrong_password_or_locked_account_cannot_login(self):
        self.assertFalse(self.client.login(username="staff", password="wrong"))
        self.staff.is_active = False
        self.staff.save(update_fields=["is_active"])
        response = self.client.post(reverse("accounts:login"), {"username": "staff", "password": "Staff-Test-938!"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post_and_ends_the_session(self):
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertEqual(self.client.get(reverse("employees:employee_list")).status_code, 302)

    def test_password_change_persists_and_keeps_current_session(self):
        self.client.force_login(self.manager)
        url = reverse("accounts:password_change")
        wrong = self.client.post(url, {"old_password": "wrong", "new_password1": "New-Secure-Cake-938!", "new_password2": "New-Secure-Cake-938!"})
        self.assertEqual(wrong.status_code, 200)
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.check_password("Manager-Test-938!"))
        response = self.client.post(url, {"old_password": "Manager-Test-938!", "new_password1": "New-Secure-Cake-938!", "new_password2": "New-Secure-Cake-938!"})
        self.assertRedirects(response, reverse("accounts:password_changed"))
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.check_password("New-Secure-Cake-938!"))
        self.assertEqual(self.client.get(reverse("employees:employee_list")).status_code, 200)


class DevLoginTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "dev-login-accounts.json"
        self.override = override_settings(DEBUG=True, CAKECRUSH_DEV_LOGIN_FILE=self.path)
        self.override.enable()
        self.addCleanup(self.override.disable)
        call_command("create_dev_accounts", stdout=StringIO())
        self.credentials = json.loads(self.path.read_text(encoding="utf-8"))

    def test_shortcuts_use_real_accounts_and_role_permissions(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, 'data-dev-role="MANAGER"')
        self.assertContains(response, 'data-dev-role="STAFF"')
        self.assertContains(response, "dev-login-accounts")
        for role, expected in [("MANAGER", "employees:employee_list"), ("STAFF", "employees:my_profile")]:
            with self.subTest(role=role):
                client = Client()
                response = client.post(reverse("accounts:login"), self.credentials[role])
                self.assertRedirects(response, reverse(expected))
                self.assertEqual(client.get(reverse("employees:employee_list")).status_code, 200 if role == "MANAGER" else 403)

    def test_production_does_not_render_credentials_or_allow_setup(self):
        with override_settings(DEBUG=False, SECURE_SSL_REDIRECT=False):
            response = self.client.get(reverse("accounts:login"))
            self.assertNotContains(response, "dev-login-accounts")
            self.assertNotContains(response, "dev-login.js")
            for entry in self.credentials.values():
                self.assertNotContains(response, entry["password"])
            with self.assertRaises(CommandError):
                call_command("create_dev_accounts", stdout=StringIO())

    def test_setup_is_idempotent_and_does_not_replace_existing_passwords(self):
        before = self.path.read_bytes()
        call_command("create_dev_accounts", stdout=StringIO())
        self.assertEqual(self.path.read_bytes(), before)
        user = get_user_model().objects.get(username="dev_staff")
        user.set_password("Changed-Development-938!")
        user.save(update_fields=["password"])
        response = self.client.get(reverse("accounts:login"))
        self.assertNotContains(response, 'data-dev-role="STAFF"')
        with self.assertRaises(CommandError):
            call_command("create_dev_accounts", stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.check_password("Changed-Development-938!"))
        self.assertEqual(self.path.read_bytes(), before)

    def test_missing_file_and_locked_accounts_do_not_offer_shortcuts(self):
        user = get_user_model().objects.get(username="dev_staff")
        user.is_active = False
        user.save(update_fields=["is_active"])
        response = self.client.get(reverse("accounts:login"))
        self.assertNotContains(response, 'data-dev-role="STAFF"')
        self.assertContains(response, 'data-dev-role="MANAGER"')
        with override_settings(CAKECRUSH_DEV_LOGIN_FILE=self.path.parent / "missing.json"):
            response = self.client.get(reverse("accounts:login"))
            self.assertNotContains(response, "dev-login-accounts")
