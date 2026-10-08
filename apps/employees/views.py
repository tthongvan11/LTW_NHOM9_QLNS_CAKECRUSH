"""Pages populated from authenticated, scoped database records."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from .access import is_manager, manager_page
from .models import Contract, Employee
from .serializers import bootstrap


# Chuẩn bị khung trang và dữ liệu đúng phạm vi người đăng nhập trước khi gửi HTML về trình duyệt.
def _page(request, template, page, **context):
    manager = is_manager(request.user)
    return render(
        request,
        template,
        {"page": page, "user_role": "manager" if manager else "staff", "bootstrap": bootstrap(request, manager), **context},
    )


@manager_page
# Trang danh sách dùng dữ liệu từ bootstrap; việc lọc/phân trang thực hiện trong employees.js.
def employee_list(request):
    return _page(request, "employees/employees/list.html", "employee-list")


@manager_page
# Mở biểu mẫu trống; thao tác lưu sau đó đi tới API, không ghi dữ liệu tại hàm này.
def employee_create(request):
    return _page(request, "employees/employees/form.html", "employee-create")


@manager_page
# Kiểm tra mã hồ sơ tồn tại trước khi gửi trang; dữ liệu chi tiết được JavaScript dựng lại.
def employee_detail(request, employee_id):
    get_object_or_404(Employee, pk=employee_id)
    return _page(
        request, "employees/employees/detail.html", "employee-detail",
        record_id=employee_id,
    )


@manager_page
# Cùng dùng biểu mẫu thêm hồ sơ; record_id giúp trình duyệt điền đúng bản ghi cần sửa.
def employee_edit(request, employee_id):
    get_object_or_404(Employee, pk=employee_id)
    return _page(
        request, "employees/employees/form.html", "employee-edit",
        record_id=employee_id,
    )


@login_required
@never_cache
@require_GET
# Phạm vi dữ liệu cá nhân được giới hạn trong serializers.bootstrap, không lấy mã nhân viên từ URL.
def my_profile(request):
    return _page(request, "employees/employees/my_profile.html", "my-profile")


@manager_page
# Danh sách nhận trạng thái do máy chủ tính; trình duyệt chỉ lọc và hiển thị các trạng thái đó.
def contract_list(request):
    return _page(request, "employees/contracts/list.html", "contract-list")


@manager_page
# Chỉ mở trang tạo hợp đồng; lựa chọn nhân viên và ô nhập được dựng trong JavaScript.
def contract_create(request):
    return _page(request, "employees/contracts/form.html", "contract-create")


@manager_page
# Mã hợp đồng không tồn tại trả về trang 404 thay vì một trang chi tiết rỗng.
def contract_detail(request, contract_id):
    get_object_or_404(Contract, pk=contract_id)
    return _page(
        request, "employees/contracts/detail.html", "contract-detail",
        record_id=contract_id,
    )


@manager_page
# Mở giao diện cập nhật; phía máy chủ chỉ cho sửa ngày gia hạn, ngày hết hạn và lương.
def contract_edit(request, contract_id):
    get_object_or_404(Contract, pk=contract_id)
    return _page(
        request, "employees/contracts/form.html", "contract-edit",
        record_id=contract_id,
    )


@login_required
@never_cache
@require_GET
# Chỉ xem hợp đồng thuộc hồ sơ liên kết với tài khoản đang đăng nhập.
def my_contracts(request):
    return _page(request, "employees/contracts/my_contracts.html", "my-contracts")
