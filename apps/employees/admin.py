from django.contrib import admin
from .models import Contract, Department, Employee


@admin.register(Department)
# Trang quản trị quản lý danh mục phòng ban, tách khỏi các trang hồ sơ của người dùng.
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_at"]
    search_fields = ["id", "name"]


@admin.register(Employee)
# Có thể liên kết tài khoản tại đây; việc vô hiệu hóa cần qua giao diện nghiệp vụ để khóa tài khoản cùng lúc.
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "department", "job", "is_active", "user"]
    list_filter = ["department", "is_active"]
    search_fields = ["id", "name", "email"]
    readonly_fields = ["id", "is_active", "end_date", "reason"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Contract)
# Mã và trạng thái được chương trình quyết định; không mở quyền xóa lịch sử trong trang quản trị.
class ContractAdmin(admin.ModelAdmin):
    list_display = ["id", "employee", "type", "start_date", "end_date", "salary"]
    list_filter = ["type"]
    search_fields = ["id", "employee__name"]
    readonly_fields = ["id", "status"]

    def has_delete_permission(self, request, obj=None):
        return False
