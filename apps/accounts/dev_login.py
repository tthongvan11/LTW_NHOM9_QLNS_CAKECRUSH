"""Local credentials for the development login shortcuts."""
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model


DEV_ROLES = (
    ("MANAGER", "dev_manager", "Quản lý"),
    ("STAFF", "dev_staff", "Nhân viên"),
)


def credential_path():
    return Path(getattr(settings, "CAKECRUSH_DEV_LOGIN_FILE", settings.BASE_DIR / ".local" / "dev-login-accounts.json"))


# Không xuất mật khẩu test khi tắt DEBUG; file mật khẩu cục bộ không được đưa vào repo.
def available_dev_accounts():
    if not settings.DEBUG:
        return []
    try:
        credentials = json.loads(credential_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(credentials, dict):
        return []
    User = get_user_model()
    accounts = []
    for role, username, label in DEV_ROLES:
        entry = credentials.get(role)
        if not isinstance(entry, dict) or entry.get("username") != username or not isinstance(entry.get("password"), str):
            continue
        user = User.objects.filter(username=username, role=role, is_active=True, is_superuser=False).first()
        # Ẩn nút nếu tài khoản bị khóa, đổi vai trò hoặc mật khẩu trong file đã không còn đúng.
        if user and user.check_password(entry["password"]):
            accounts.append({"role": role, "label": label, "username": username, "password": entry["password"]})
    return accounts
