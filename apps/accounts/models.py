"""Authentication foundation for the NGUOIDUNG entity."""
from django.contrib.auth.models import AbstractUser
from django.db import models


# Tài khoản dùng đăng nhập chung cho website; role là quyền nghiệp vụ, không tự cấp quyền vào trang Django Admin.
class User(AbstractUser):
    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Người quản lý"
        STAFF = "STAFF", "Nhân viên"

    role = models.CharField(
        "Vai trò",
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF,
    )

    class Meta:
        db_table = "NGUOIDUNG"
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
