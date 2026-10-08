from django.contrib.auth import views as auth_views
from django.urls import reverse

from .dev_login import available_dev_accounts


# Dùng cơ chế kiểm tra mật khẩu/phiên đăng nhập có sẵn của Django; chỉ bổ sung giao diện và nơi chuyển tiếp.
class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    # Thông tin test chỉ xuất hiện khi hàm available_dev_accounts xác nhận môi trường và tài khoản còn hợp lệ.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dev_accounts"] = available_dev_accounts()
        return context

    # Khi không có địa chỉ next hợp lệ, quản lý vào danh sách và nhân viên vào hồ sơ cá nhân.
    def get_default_redirect_url(self):
        user = self.request.user
        return reverse("employees:employee_list" if user.role == "MANAGER" or user.is_superuser else "employees:my_profile")
