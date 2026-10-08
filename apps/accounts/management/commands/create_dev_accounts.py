"""Create dedicated accounts used by development login shortcuts."""
import json
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.dev_login import DEV_ROLES, available_dev_accounts, credential_path


class Command(BaseCommand):
    help = "Tạo hai tài khoản test cho nút chọn vai trò trên trang đăng nhập dev."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Chỉ sử dụng lệnh này trong môi trường phát triển.")
        output = credential_path()
        if output.exists():
            if len(available_dev_accounts()) == len(DEV_ROLES):
                self.stdout.write(self.style.SUCCESS("Development test accounts are ready; existing passwords preserved."))
                return
            raise CommandError("Thông tin test hiện có không khớp tài khoản. Tài khoản và mật khẩu được giữ nguyên.")
        User = get_user_model()
        if User.objects.filter(username__in=[username for _, username, _ in DEV_ROLES]).exists():
            raise CommandError("Tên tài khoản test đã tồn tại. Không thay đổi mật khẩu của tài khoản hiện có.")
        output.parent.mkdir(parents=True, exist_ok=True)
        credentials = {}
        with transaction.atomic():
            for role, username, label in DEV_ROLES:
                password = secrets.token_urlsafe(18)
                User.objects.create_user(username=username, password=password, role=role, first_name=label, last_name="test")
                credentials[role] = {"username": username, "password": password}
            # Exclusive creation prevents replacing an existing local credential file.
            with output.open("x", encoding="utf-8") as target:
                json.dump(credentials, target, indent=2)
        self.stdout.write(self.style.SUCCESS("Created development test accounts. Login shortcuts are ready."))
