from django.urls import path

from . import api, views

app_name = "employees"

# Địa chỉ api nhận thao tác ghi; các địa chỉ còn lại mở trang xem/biểu mẫu. Mã trên URL được chuyển vào hàm xử lý.
urlpatterns = [
    path("api/employees/", api.employee_save, name="employee_save"),
    path("api/employees/<slug:employee_id>/", api.employee_save, name="employee_update"),
    path("api/employees/<slug:employee_id>/deactivate/", api.employee_deactivate, name="employee_deactivate"),
    path("api/contracts/", api.contract_save, name="contract_save"),
    path("api/contracts/<slug:contract_id>/", api.contract_save, name="contract_update"),
    path("", views.employee_list, name="employee_list"),
    path("new/", views.employee_create, name="employee_create"),
    path("me/", views.my_profile, name="my_profile"),
    path("me/contracts/", views.my_contracts, name="my_contracts"),
    path("contracts/", views.contract_list, name="contract_list"),
    path("contracts/new/", views.contract_create, name="contract_create"),
    path("contracts/<slug:contract_id>/edit/", views.contract_edit, name="contract_edit"),
    path("contracts/<slug:contract_id>/", views.contract_detail, name="contract_detail"),
    path("<slug:employee_id>/edit/", views.employee_edit, name="employee_edit"),
    path("<slug:employee_id>/", views.employee_detail, name="employee_detail"),
]
