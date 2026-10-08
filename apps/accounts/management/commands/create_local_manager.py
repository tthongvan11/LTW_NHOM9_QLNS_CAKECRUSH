"""Create an initial local manager without embedding a password in source code."""
import json
import re
import secrets
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Tạo tài khoản quản lý cục bộ và lưu thông tin đăng nhập trong .local/."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="cakecrush_admin")
        parser.add_argument("--output", default="local-manager-login.json")

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Chỉ sử dụng lệnh này cho môi trường phát triển cục bộ.")
        username = options["username"]
        filename = options["output"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", username) or not re.fullmatch(r"[A-Za-z0-9_-]+\.json", filename):
            raise CommandError("Tên tài khoản hoặc tên tệp không hợp lệ.")
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise CommandError("Tài khoản đã tồn tại; mật khẩu hiện tại được giữ nguyên.")
        output = Path(settings.BASE_DIR) / ".local" / filename
        if output.exists():
            raise CommandError("Tệp thông tin đăng nhập đã tồn tại. Hãy chọn tên tệp khác.")
        password = secrets.token_urlsafe(18)
        output.parent.mkdir(parents=True, exist_ok=True)
        with transaction.atomic():
            User.objects.create_superuser(username=username, password=password, role="MANAGER", first_name="Quản lý", last_name="Cake Crush")
            output.write_text(json.dumps({"username": username, "password": password, "login_url": "/accounts/login/"}, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Created local manager. Credentials: {output}"))
