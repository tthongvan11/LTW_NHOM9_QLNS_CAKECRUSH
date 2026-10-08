import json
import logging
from functools import wraps
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from .access import is_manager
from .forms import ContractForm, ContractUpdateForm, DeactivateForm, EmployeeForm
from .models import Contract, Employee

logger = logging.getLogger(__name__)


# Lớp kiểm tra chung cho mọi thao tác ghi; CSRF vẫn được Django kiểm tra trước khi tới đây.
def mutation(view):
    @wraps(view)
    @never_cache
    @require_POST
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Phiên đăng nhập đã hết. Vui lòng đăng nhập lại."}, status=401)
        if not is_manager(request.user):
            return JsonResponse({"error": "Chỉ người quản lý được thay đổi dữ liệu."}, status=403)
        if request.content_type != "application/json":
            return JsonResponse({"error": "Dữ liệu gửi không đúng định dạng."}, status=400)
        # JSON phải là một bộ tên trường/giá trị chuỗi, đúng dạng dữ liệu biểu mẫu gửi từ trình duyệt.
        try:
            data = json.loads(request.body)
            if not isinstance(data, dict) or any(not isinstance(value, str) for value in data.values()):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({"error": "Dữ liệu gửi không đúng định dạng."}, status=400)
        try:
            # Nhóm các thay đổi thành một lần lưu: có lỗi thì hoàn tác, tránh hồ sơ/tài khoản bị cập nhật dở dang.
            with transaction.atomic():
                return view(request, data, *args, **kwargs)
        except ValidationError as exc:
            return JsonResponse({"error": " · ".join(exc.messages)}, status=400)
        # Bảng vẫn có thể từ chối dữ liệu trùng dù biểu mẫu đã kiểm tra, chẳng hạn hai người lưu cùng lúc.
        except IntegrityError:
            return JsonResponse({"error": "Dữ liệu bị trùng hoặc không hợp lệ. Vui lòng kiểm tra CCCD, email và số điện thoại."}, status=409)
        except DatabaseError:
            logger.exception("HR database write failed")
            return JsonResponse({"error": "Không thể lưu vào database. Vui lòng thử lại."}, status=503)
    return wrapper


# Biểu mẫu kiểm tra dữ liệu và quy tắc của model; chỉ dữ liệu hợp lệ mới được lưu và báo thành công.
def save_form(request, form, message):
    if not form.is_valid():
        errors = {field: list(values) for field, values in form.errors.items()}
        return JsonResponse({"error": " · ".join(value for values in errors.values() for value in values), "errors": errors}, status=400)
    item = form.save()
    messages.success(request, message)
    return JsonResponse({"id": item.pk})


@mutation
# Có mã thì sửa hồ sơ đã có; không có mã thì tạo mới. Mã nhân viên không lấy từ dữ liệu gửi lên.
def employee_save(request, data, employee_id=None):
    item = get_object_or_404(Employee.objects.select_for_update(), pk=employee_id) if employee_id else None
    return save_form(request, EmployeeForm(data, instance=item), "Đã cập nhật hồ sơ nhân viên." if item else "Đã thêm hồ sơ nhân viên.")


@mutation
# Vô hiệu hóa giữ hồ sơ/hợp đồng và khóa tài khoản liên kết, không xóa lịch sử hay tự chấm dứt hợp đồng.
def employee_deactivate(request, data, employee_id):
    item = get_object_or_404(Employee.objects.select_for_update(), pk=employee_id)
    if not item.is_active:
        return JsonResponse({"error": "Hồ sơ này đã được vô hiệu hóa."}, status=409)
    # Không cho người dùng vô hiệu hóa chính tài khoản đang thực hiện thao tác.
    if item.user_id == request.user.pk:
        return JsonResponse({"error": "Bạn không thể vô hiệu hóa tài khoản đang đăng nhập của mình."}, status=400)
    form = DeactivateForm(data, employee=item)
    if not form.is_valid():
        return JsonResponse({"error": " · ".join(value for values in form.errors.values() for value in values)}, status=400)
    item.is_active = False
    item.end_date = form.cleaned_data["end_date"]
    item.reason = form.cleaned_data["reason"]
    item.save()
    # Khóa tài khoản trong cùng giao dịch với hồ sơ; các lần xác thực sau sẽ không chấp nhận tài khoản này.
    if item.user_id:
        item.user.is_active = False
        item.user.save(update_fields=["is_active"])
    messages.success(request, f"Đã vô hiệu hóa hồ sơ {item.pk}.")
    return JsonResponse({"id": item.pk})


@mutation
# Tạo và cập nhật dùng hai biểu mẫu khác nhau để khóa các thông tin gốc của hợp đồng khi gia hạn.
def contract_save(request, data, contract_id=None):
    item = get_object_or_404(Contract.objects.select_for_update(), pk=contract_id) if contract_id else None
    if item:
        if not item.employee.is_active or item.status == Contract.Status.TERMINATED:
            return JsonResponse({"error": "Không thể gia hạn hợp đồng đã chấm dứt hoặc của nhân viên đã nghỉ việc."}, status=400)
        form = ContractUpdateForm(data, instance=item)
    else:
        form = ContractForm(data)
    return save_form(request, form, "Đã cập nhật hợp đồng lao động." if item else "Đã tạo hợp đồng lao động.")
