from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Contract, Department, Employee


# Danh sách fields là các thông tin được phép ghi từ giao diện; trường tài khoản/trạng thái không nằm trong danh sách.
class EmployeeForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), to_field_name="name", label="Phòng ban")

    class Meta:
        model = Employee
        fields = ["name", "birth_date", "gender", "identity", "phone", "email", "address", "department", "job", "start_date"]

    # Chuẩn hóa email và kiểm tra cả hồ sơ đã nghỉ việc; khi sửa bỏ qua chính hồ sơ hiện tại.
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Employee.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Email đã được sử dụng trong một hồ sơ khác.")
        return email


# Chỉ chọn nhân viên đang làm việc; nhãn loại hợp đồng trên giao diện sẽ được đổi sang mã lưu trong bảng.
class ContractForm(forms.ModelForm):
    employee_id = forms.ModelChoiceField(queryset=Employee.objects.filter(is_active=True), label="Nhân viên")
    type = forms.ChoiceField(choices=[(label, label) for _, label in Contract.Type.choices], label="Loại hợp đồng")

    class Meta:
        model = Contract
        fields = ["type", "signed_date", "start_date", "end_date", "salary"]

    # Ví dụ nhãn Thử việc được đổi thành THU_VIEC để lưu thống nhất trong database.
    def clean_type(self):
        return {label: value for value, label in Contract.Type.choices}[self.cleaned_data["type"]]

    # Gắn nhân viên đã kiểm tra vào hợp đồng trước khi Django gọi phần kiểm tra quy tắc của model.
    def clean(self):
        data = super().clean()
        if data.get("employee_id"):
            self.instance.employee = data["employee_id"]
        return data


# Giới hạn ba trường được sửa; gửi thêm mã nhân viên/loại/ngày bắt đầu cũng không đổi được các trường gốc.
class ContractUpdateForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["renewal_date", "end_date", "salary"]


# Thu ngày/lý do nghỉ việc; hàm API sẽ dùng kết quả sạch để đổi trạng thái hồ sơ.
class DeactivateForm(forms.Form):
    end_date = forms.DateField(label="Ngày nghỉ việc")
    reason = forms.CharField(label="Lý do nghỉ việc", max_length=500)

    def __init__(self, *args, employee, **kwargs):
        super().__init__(*args, **kwargs)
        self.employee = employee

    # Ngày nghỉ việc phải nằm từ ngày vào làm đến ngày hiện tại theo giờ của máy chủ.
    def clean_end_date(self):
        value = self.cleaned_data["end_date"]
        if value < self.employee.start_date or value > timezone.localdate():
            raise ValidationError("Ngày nghỉ việc phải từ ngày vào làm đến ngày hiện tại.")
        return value
