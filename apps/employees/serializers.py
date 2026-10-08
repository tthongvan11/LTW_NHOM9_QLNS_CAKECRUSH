from django.contrib.messages import get_messages
from .models import Contract, Department, Employee


# Đổi ngày thành YYYY-MM-DD để ô nhập ngày và phép so sánh trên trình duyệt dùng được; thiếu ngày trả chuỗi rỗng.
def date_value(value):
    return value.isoformat() if value else ""


# Chỉ chuyển các thông tin giao diện cần; liên kết phòng ban được đổi thành tên để người dùng dễ đọc.
def employee_data(item):
    return {"id": item.pk, "name": item.name, "department": item.department.name,
            "job": item.job, "gender": item.gender, "birth_date": date_value(item.birth_date),
            "identity": item.identity, "phone": item.phone, "email": item.email,
            "address": item.address, "start_date": date_value(item.start_date),
            "status": "active" if item.is_active else "inactive",
            "end_date": date_value(item.end_date), "reason": item.reason}


# Lương gửi dưới dạng chuỗi để không làm tròn khi hiển thị; trạng thái được tính tại máy chủ.
def contract_data(item):
    return {"id": item.pk, "employee_id": item.employee_id, "type": item.get_type_display(),
            "signed_date": date_value(item.signed_date), "start_date": date_value(item.start_date),
            "end_date": date_value(item.end_date), "renewal_date": date_value(item.renewal_date),
            "salary": str(item.salary), "status": item.display_status}


# Gói dữ liệu lần mở trang: quản lý thấy toàn bộ, nhân viên chỉ thấy hồ sơ/hợp đồng của tài khoản mình.
def bootstrap(request, manager):
    employees = Employee.objects.select_related("department").all()
    contracts = Contract.objects.all()
    # Giới hạn trước khi gửi sang trình duyệt; ẩn hàng bằng JavaScript không thể thay thế bước bảo vệ này.
    if not manager:
        employees = employees.filter(user=request.user)
        contracts = contracts.filter(employee__user=request.user)
    # Có thể chưa liên kết hồ sơ: currentUser sẽ rỗng và trang cá nhân hiện thông báo thay vì dùng nhân viên giả.
    own = Employee.objects.select_related("department").filter(user=request.user).first()
    name = own.name if own else request.user.get_full_name() or request.user.username
    return {
        "employees": [employee_data(item) for item in employees],
        "contracts": [contract_data(item) for item in contracts],
        "departments": list(Department.objects.values_list("name", flat=True)),
        "jobs": sorted(set(Employee.objects.values_list("job", flat=True))) if manager else [],
        "creationTypes": list(Contract.Type.labels), "types": list(Contract.Type.labels),
        "currentUser": employee_data(own) if own else None,
        "account": {"name": name, "job": own.job if own else ("Quản lý nhân sự" if manager else "Nhân viên"), "initials": "".join(part[0] for part in name.split()[-2:]).upper()},
        # Đọc thông báo sau lần lưu trước để JavaScript hiện kết quả khi trang danh sách được tải lại.
        "messages": [str(message) for message in get_messages(request)],
    }
