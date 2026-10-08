"""Project URL configuration; business routes are added within each app."""
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Quản trị Cake Crush"
admin.site.site_title = "Cake Crush"
admin.site.index_title = "Quản trị hệ thống"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    # Chuyển mọi địa chỉ bắt đầu bằng employees/ sang các đường dẫn của module hồ sơ/hợp đồng.
    path("employees/", include("apps.employees.urls")),
    path("attendance/", include("apps.attendance.urls")),
    path("training/", include("apps.training.urls")),
    path("performance/", include("apps.performance.urls")),
]
