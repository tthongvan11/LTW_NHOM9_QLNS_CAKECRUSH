from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


# Quyền được đọc từ tài khoản đã xác thực; tham số trên địa chỉ trang không cấp quyền.
def is_manager(user):
    return user.is_authenticated and user.is_active and (user.role == "MANAGER" or user.is_superuser)


# Bọc trang quản lý: yêu cầu đăng nhập, chỉ nhận thao tác xem và từ chối Nhân viên.
def manager_page(view):
    @wraps(view)
    @login_required
    @never_cache
    @require_GET
    def wrapper(request, *args, **kwargs):
        if not is_manager(request.user):
            raise PermissionDenied("Chỉ người quản lý được truy cập chức năng này.")
        return view(request, *args, **kwargs)
    return wrapper
