# Cấu trúc dự án Cake Crush

Cấu trúc được đối chiếu với phần Phân tích quy trình, Use Case và ERD trong tài liệu **50K22.2-Nhom9-ChuDe5-BCTD2-1.docx**. Các nội dung mô tả trong tài liệu được dùng làm yêu cầu nghiệp vụ tham khảo cho bộ khung.

## Cách chia Django project và Django app

`config/` là Django project, chứa cấu hình, URL gốc và điểm chạy WSGI/ASGI. `apps/` chứa các Django app theo phạm vi nghiệp vụ. Việc đặt app trong `apps/` được khai báo bằng tên đầy đủ trong `AppConfig.name` và `INSTALLED_APPS`.

Hai phần Tài khoản và Dashboard cùng thuộc nhóm chức năng 1 trong đặc tả, nhưng tách thành `accounts` và `dashboard` vì xác thực và tổng hợp thống kê có trách nhiệm khác nhau. Hồ sơ và hợp đồng nằm chung trong `employees`; chấm công và nghỉ phép nằm chung trong `attendance`; đánh giá, phản hồi và khen thưởng/kỷ luật nằm chung trong `performance`.

`core` giữ trang khởi đầu và các thành phần dùng chung, không nhận nghiệp vụ vốn thuộc một phân hệ khác.

## Đối chiếu nhóm chức năng

| Nhóm trong đặc tả | App | Phần sẽ phát triển |
| --- | --- | --- |
| 1. Quản trị tài khoản, phân quyền và Dashboard | `accounts`, `dashboard` | Đăng nhập/đăng xuất, cập nhật tài khoản, vai trò quản lý/nhân viên; thống kê nhân sự, chấm công, phép, hợp đồng sắp hết hạn và đào tạo |
| 2. Quản lý hồ sơ và hợp đồng lao động | `employees` | Tạo/xem/sửa/vô hiệu hóa hồ sơ, lọc theo bộ phận, quản lý hợp đồng và xem hồ sơ/hợp đồng của bản thân |
| 3. Chấm công và quản lý phép | `attendance` | Check-in/out, lịch sử, tổng hợp và xuất bảng công, gửi/duyệt/từ chối đơn, theo dõi quỹ phép |
| 4. Đào tạo nội bộ | `training` | Tạo/sửa khóa học, phân công, xác nhận hoàn thành và cập nhật kết quả |
| 5. Đánh giá và khen thưởng | `performance` | Tạo kỳ, thiết lập tiêu chí, chấm điểm, công bố kết quả, phản hồi, khen thưởng và kỷ luật |

## Vị trí của 15 thực thể ERD

| Thực thể | Vị trí model |
| --- | --- |
| NGUOIDUNG | `apps/accounts/models.py` |
| PHONGBAN | `apps/employees/models.py` |
| NHANVIEN | `apps/employees/models.py` |
| HOPDONG | `apps/employees/models.py` |
| CHAMCONG | `apps/attendance/models.py` |
| DONNGHIPHEP | `apps/attendance/models.py` |
| LOAIPHEP | `apps/attendance/models.py` |
| DAOTAO | `apps/training/models.py` |
| NV_DAOTAO | `apps/training/models.py` |
| KYDANHGIA | `apps/performance/models.py` |
| TIEUCHI | `apps/performance/models.py` |
| DANHGIA | `apps/performance/models.py` |
| CHITIETDANHGIA | `apps/performance/models.py` |
| KHENTHUONG_KYLUAT | `apps/performance/models.py` |
| PHANHOI | `apps/performance/models.py` |

Đây là bản phân bổ vị trí. Đã triển khai `accounts.User`, `employees.Department`, `employees.Employee` và `employees.Contract`. Các thực thể ở những phân hệ khác sẽ phát triển tiếp.

Dashboard lấy dữ liệu từ các phân hệ. Quỹ phép được tổ chức trong `attendance`; cấu trúc hiện tại không bổ sung bảng ngoài ERD.

## Tài khoản cơ sở

Bộ khung dùng `accounts.User(AbstractUser)` ngay từ đầu và đặt `AUTH_USER_MODEL = "accounts.User"`. Đây là nền tảng cho việc mở rộng tài khoản theo [hướng dẫn chính thức của Django](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project).

| Thuộc tính trong đặc tả NGUOIDUNG | Thuộc tính trong model |
| --- | --- |
| id_taikhoan | `id` do Django tạo |
| tendangnhap | `username` kế thừa từ AbstractUser |
| matkhau | `password`, sử dụng cơ chế băm mật khẩu của Django |
| vaitro | `role`, có lựa chọn MANAGER và STAFF, mặc định STAFF |
| trangthai_hoatdong | `is_active` |
| ngaytao | `date_joined` |

Tên bảng được đặt là `NGUOIDUNG`. Các cột dùng tên của Django như bảng đối chiếu trên; bộ khung chưa phải bản triển khai toàn bộ ERD. Các trường bổ sung của Django hỗ trợ quản trị, quyền và xác thực.

NHANVIEN liên kết tài khoản bằng `models.OneToOneField(settings.AUTH_USER_MODEL, ...)`. Bảng quan hệ trong đặc tả mô tả liên kết 1–1; bảng chi tiết thuộc tính cho phép liên kết tài khoản để trống khi tạo hồ sơ trước lúc cấp tài khoản. Model hiện dùng `null=True, blank=True` và `on_delete=PROTECT` cho liên kết này.

Vai trò nghiệp vụ không tự cấp quyền truy cập một view và không tự cấp quyền vào Django Admin. Các trang/API hồ sơ và hợp đồng đã kiểm tra quyền quản lý và giới hạn nhân viên vào dữ liệu của bản thân.

## Giao diện và tệp

- `templates/base.html`: khung HTML chung.
- `templates/includes/`: các phần có thể tái sử dụng.
- `templates/<app_name>/`: giao diện của từng phân hệ.
- `templates/<app_name>/<feature>/`: chia tiếp theo chức năng như hồ sơ, phòng ban, hợp đồng, chấm công, nghỉ phép, khóa học và đánh giá.
- `templates/employees/base.html`: bố cục hồ sơ/hợp đồng theo Figma, sidebar, header, menu tài khoản và hộp xác nhận vô hiệu hóa.
- `templates/employees/employees/`: danh sách, chi tiết, biểu mẫu thêm/sửa và hồ sơ của tôi.
- `templates/employees/contracts/`: danh sách, chi tiết, biểu mẫu tạo/gia hạn và hợp đồng của tôi.
- `static/css/employees.css`, `static/js/employees.js`: bố cục thu gọn và tương tác. Django cung cấp dữ liệu từ ORM và API POST lưu vào SQLite; không dùng dữ liệu demo hoặc sessionStorage.
- `static/css/`, `static/js/`, `static/images/`, `static/icons/`: tài nguyên mã nguồn.
- `media/avatars/`: nơi dự kiến lưu ảnh hồ sơ.
- `media/contracts/`: nơi dự kiến lưu tệp hợp đồng.
- `media/training/`: nơi dự kiến lưu tài liệu đào tạo.
- `staticfiles/`: được tạo khi chạy `collectstatic`, không đưa vào mã nguồn.
- `db.sqlite3`: được tạo khi chạy `migrate`, không đưa vào mã nguồn.

Các thư mục trống có `.gitkeep` để lưu cây thư mục trong Git. Tệp tải lên không được đưa vào Git. Chưa triển khai tải lên hoặc phục vụ tệp nhân sự.

## Cây tệp đầy đủ

```text
LTW_NHOM9_QLNS_CAKECRUSH/
├── apps/
│   ├── accounts/
│   │   ├── management/
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   └── create_local_manager.py
│   │   │   └── __init__.py
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── attendance/
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── core/
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── dashboard/
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── employees/
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_departments.py
│   │   │   ├── 0003_remove_contract_contract_valid_end_date_and_more.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── access.py
│   │   ├── admin.py
│   │   ├── api.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── performance/
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── training/
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── __init__.py
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docs/
│   ├── database.md
│   └── project_structure.md
├── media/
│   ├── avatars/
│   │   └── .gitkeep
│   ├── contracts/
│   │   └── .gitkeep
│   └── training/
│       └── .gitkeep
├── static/
│   ├── css/
│   │   ├── base.css
│   │   └── employees.css
│   ├── fonts/
│   │   └── inter/
│   │       ├── inter-0.ttf
│   │       ├── inter-1.ttf
│   │       ├── inter-2.ttf
│   │       ├── inter-3.ttf
│   │       ├── inter.css
│   │       └── OFL.txt
│   ├── icons/
│   │   ├── employees/
│   │   │   ├── bell.svg
│   │   │   ├── book.svg
│   │   │   ├── briefcase.svg
│   │   │   ├── cake.svg
│   │   │   ├── calendar.svg
│   │   │   ├── chevron.svg
│   │   │   ├── clock.svg
│   │   │   ├── file.svg
│   │   │   ├── home.svg
│   │   │   ├── lock.svg
│   │   │   ├── logout.svg
│   │   │   ├── map-pin.svg
│   │   │   ├── search.svg
│   │   │   ├── shield.svg
│   │   │   ├── star.svg
│   │   │   ├── user.svg
│   │   │   └── users.svg
│   │   └── .gitkeep
│   ├── images/
│   │   └── .gitkeep
│   └── js/
│       ├── employees.js
│       └── main.js
├── templates/
│   ├── accounts/
│   │   ├── .gitkeep
│   │   ├── login.html
│   │   ├── password_change.html
│   │   └── password_changed.html
│   ├── attendance/
│   │   ├── leave_balances/
│   │   │   └── .gitkeep
│   │   ├── leave_requests/
│   │   │   └── .gitkeep
│   │   └── records/
│   │       └── .gitkeep
│   ├── core/
│   │   └── home.html
│   ├── dashboard/
│   │   └── .gitkeep
│   ├── employees/
│   │   ├── contracts/
│   │   │   ├── .gitkeep
│   │   │   ├── detail.html
│   │   │   ├── form.html
│   │   │   ├── list.html
│   │   │   └── my_contracts.html
│   │   ├── departments/
│   │   │   └── .gitkeep
│   │   ├── employees/
│   │   │   ├── detail.html
│   │   │   ├── form.html
│   │   │   ├── list.html
│   │   │   └── my_profile.html
│   │   ├── includes/
│   │   │   └── icon.html
│   │   └── base.html
│   ├── includes/
│   │   ├── header.html
│   │   └── messages.html
│   ├── performance/
│   │   ├── criteria/
│   │   │   └── .gitkeep
│   │   ├── evaluations/
│   │   │   └── .gitkeep
│   │   ├── periods/
│   │   │   └── .gitkeep
│   │   └── rewards_discipline/
│   │       └── .gitkeep
│   ├── training/
│   │   ├── assignments/
│   │   │   └── .gitkeep
│   │   └── courses/
│   │       └── .gitkeep
│   ├── 403.html
│   ├── 404.html
│   └── base.html
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

Không liệt kê Git, cấu hình IDE, môi trường Python, database sinh ra hoặc thư mục .local chứa tài khoản và dữ liệu kiểm thử cục bộ.

## Thứ tự triển khai đề xuất

1. Hoàn thiện xác thực và kiểm tra vai trò trong `accounts`.
2. Triển khai phòng ban, hồ sơ nhân viên và hợp đồng trong `employees`.
3. Triển khai chấm công, loại phép, đơn nghỉ phép và các phép tính liên quan trong `attendance`.
4. Triển khai khóa đào tạo và bảng phân công trong `training`.
5. Triển khai kỳ đánh giá, tiêu chí, điểm, phản hồi và thưởng/phạt trong `performance`.
6. Tổng hợp dữ liệu thực tế lên `dashboard`.

Mỗi phân hệ bổ sung model, biểu mẫu, view, URL và kiểm thử nghiệp vụ tại các vị trí đã tạo. Hồ sơ và hợp đồng đã có model, migration, ModelForm, view/API, xác thực/phân quyền và kiểm thử. Các phân hệ khác vẫn là bộ khung. Xem [hướng dẫn database](database.md).
