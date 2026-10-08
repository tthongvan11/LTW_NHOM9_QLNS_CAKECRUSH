# Quản lý nhân sự Cake Crush

Hướng dẫn dành cho Nhóm 9: vị trí các file, phần việc của từng thành viên và cách chạy dự án. Phạm vi dựa trên tài liệu **50K22.2-Nhom9-ChuDe5-BCTD2-1.docx**.

**Đã hoạt động:** đăng nhập/đăng xuất, đổi mật khẩu, quyền Quản lý/Nhân viên; hồ sơ và hợp đồng lưu vào database; nút đăng nhập nhanh và bộ dữ liệu mẫu.

**Còn phát triển:** Dashboard, Chấm công/Phép, Đào tạo, Đánh giá/Khen thưởng. Các phần này mới có thư mục. Quản trị tài khoản/phòng ban hiện dùng trang Django Admin.

## 1. Cấu trúc dự án

Ba nơi làm việc chính: **`apps/` xử lý và lưu dữ liệu**, **`templates/` dựng các trang**, **`static/` chỉnh hình thức và thao tác trên trang**.

### Thư mục và file chung

```text
LTW_NHOM9_QLNS_CAKECRUSH/
├── apps/                  # Các phần chức năng, xem phân công ở mục 3
│   ├── accounts/          # Tài khoản, đăng nhập và quyền sử dụng
│   ├── dashboard/         # Trang tổng quan, tổng hợp số liệu
│   ├── employees/         # Phòng ban, hồ sơ và hợp đồng
│   ├── attendance/        # Chấm công, đơn nghỉ phép và quỹ phép
│   ├── training/          # Khóa đào tạo, phân công và kết quả học
│   ├── performance/       # Đánh giá, phản hồi, khen thưởng/kỷ luật
│   └── core/              # Trang khởi đầu và phần xử lý dùng chung
├── config/                # Thiết lập toàn website
│   ├── settings.py        # Database, ngôn ngữ, giờ, đăng nhập, thư mục
│   ├── urls.py            # Nối địa chỉ của các phần chức năng
│   ├── asgi.py            # Điểm chạy website khi triển khai lên máy chủ
│   ├── wsgi.py            # Điểm chạy website theo cách triển khai thông thường
│   └── __init__.py        # Đánh dấu thư mục Python, thường không cần sửa
├── templates/             # File giao diện .html, xem cây bên dưới
├── static/                # Kiểu dáng, thao tác, ảnh, biểu tượng, phông chữ
├── media/                 # Dự kiến lưu file người dùng tải lên
│   ├── avatars/           # Ảnh hồ sơ
│   ├── contracts/         # Tệp hợp đồng
│   └── training/          # Tài liệu đào tạo
├── docs/                  # Hướng dẫn chi tiết
│   ├── database.md        # Database, tài khoản, dữ liệu mẫu, kiểm tra
│   └── project_structure.md # Cấu trúc và đối chiếu đặc tả
├── manage.py              # Chạy các lệnh của dự án
├── requirements.txt       # Danh sách thư viện cần cài
├── .env.example           # Mẫu thiết lập cho máy cá nhân
├── .gitignore             # Các file không đưa lên repo
└── README.md              # Hướng dẫn này
```

Các phần tự tạo trên mỗi máy: `.venv/` chứa thư viện Python; `.env` chứa thiết lập riêng; `db.sqlite3` chứa database; `.local/` chứa mật khẩu test và bản sao lưu. `staticfiles/` được tạo khi chuẩn bị đưa website lên máy chủ. Những phần này không đưa lên repo.

### File trong mỗi phần chức năng

Mỗi thư mục con của `apps/` đều có các file dưới đây. Ví dụ, Hồng Vân sửa `apps/employees/models.py`, còn Như sửa `apps/attendance/models.py`.

| File/thư mục | Chức năng và phạm vi |
| --- | --- |
| `models.py` | Khai báo thông tin cần lưu, các bảng và quan hệ của phần mình phụ trách. |
| `forms.py` | Khai báo ô nhập và kiểm tra thông tin người dùng nhập. |
| `views.py` | Chọn trang hiển thị, lấy dữ liệu và xử lý yêu cầu. |
| `urls.py` | Khai báo địa chỉ dẫn đến từng chức năng. |
| `admin.py` | Cho phép quản trị viên quản lý các bảng trong Django Admin. |
| `tests.py` | Kiểm tra chức năng, quyền truy cập và việc lưu dữ liệu. |
| `apps.py` | Khai báo tên phần chức năng để Django nhận diện. |
| `migrations/` | Lưu các thay đổi cấu trúc bảng; Django tạo file bằng `makemigrations`. |
| `__init__.py` | Đánh dấu thư mục Python, thường để trống; áp dụng cả ở `apps/` và các thư mục con. |

Các file bổ sung đang có:

| Vị trí | Chức năng |
| --- | --- |
| `apps/accounts/dev_login.py` | Đọc tài khoản test hợp lệ để hiện nút chọn vai trò. |
| `apps/accounts/management/commands/create_dev_accounts.py` | Tạo hai tài khoản test Quản lý/Nhân viên. |
| `apps/accounts/management/commands/create_local_manager.py` | Tạo quản trị viên ban đầu cho máy cá nhân. |
| `apps/accounts/migrations/0001_initial.py` | Tạo bảng tài khoản. |
| `apps/employees/access.py` | Kiểm tra quyền vào các trang quản lý. |
| `apps/employees/api.py` | Nhận thông tin từ giao diện để lưu hồ sơ/hợp đồng. |
| `apps/employees/serializers.py` | Chuẩn bị dữ liệu hiển thị theo quyền của người đăng nhập. |
| `apps/employees/sample_data/hr_demo.json` | Bộ dữ liệu giả lập dùng chung trong repo. |
| `apps/employees/management/commands/seed_demo_data.py` | Nạp bộ mẫu vào database trên máy đang chạy. |
| `apps/employees/migrations/0001_initial.py` | Tạo bảng phòng ban, nhân viên, hợp đồng. |
| `apps/employees/migrations/0002_departments.py` | Tạo sáu phòng ban ban đầu. |
| `apps/employees/migrations/0003_remove_contract_contract_valid_end_date_and_more.py` | Bổ sung kiểm tra ngày hết hạn hợp đồng. |

`management/commands/` chứa các lệnh chạy bằng `manage.py`; các file `__init__.py` bên trong giúp Django tìm được lệnh.

### File giao diện

```text
templates/
├── base.html                    # Khung trang chung
├── 403.html                     # Thông báo không có quyền truy cập
├── 404.html                     # Thông báo không tìm thấy trang/bản ghi
├── includes/
│   ├── header.html              # Phần đầu trang dùng chung
│   └── messages.html            # Thông báo kết quả thao tác
├── core/home.html               # Trang giới thiệu dự án
├── accounts/
│   ├── login.html               # Đăng nhập và nút chọn vai trò test
│   ├── password_change.html     # Đổi mật khẩu
│   └── password_changed.html    # Thông báo đổi mật khẩu thành công
├── dashboard/                   # Dự kiến giao diện tổng quan
├── employees/
│   ├── base.html                # Menu, tài khoản, hộp xác nhận của Hồ sơ/Hợp đồng
│   ├── includes/icon.html       # Hiển thị biểu tượng
│   ├── employees/
│   │   ├── list.html            # Danh sách, tìm kiếm, lọc nhân viên
│   │   ├── detail.html          # Chi tiết hồ sơ
│   │   ├── form.html            # Thêm/sửa hồ sơ
│   │   └── my_profile.html      # Nhân viên xem hồ sơ của mình
│   ├── contracts/
│   │   ├── list.html            # Danh sách, lọc, cảnh báo hợp đồng
│   │   ├── detail.html          # Chi tiết hợp đồng
│   │   ├── form.html            # Tạo/chỉnh sửa/gia hạn hợp đồng
│   │   └── my_contracts.html    # Nhân viên xem hợp đồng của mình
│   └── departments/             # Dự kiến giao diện phòng ban
├── attendance/
│   ├── records/                 # Chấm công
│   ├── leave_requests/          # Gửi và xét duyệt đơn nghỉ phép
│   └── leave_balances/          # Theo dõi quỹ phép
├── training/
│   ├── courses/                 # Khóa đào tạo và nội dung học
│   └── assignments/             # Phân công, tiến độ, kết quả học
└── performance/
    ├── periods/                 # Kỳ đánh giá
    ├── criteria/                # Tiêu chí đánh giá
    ├── evaluations/             # Điểm, kết quả và phản hồi
    └── rewards_discipline/      # Khen thưởng và kỷ luật
```

Các thư mục ghi “dự kiến” và các thư mục của UC3–5 hiện chỉ có `.gitkeep` để giữ vị trí trong repo. File `.gitkeep` không tạo chức năng. Việc tải file lên `media/` cũng chưa triển khai.

| Tài nguyên trong `static/` | Chức năng |
| --- | --- |
| `css/base.css` | Kiểu dáng các trang dùng khung chung. |
| `css/employees.css` | Kiểu dáng Hồ sơ/Hợp đồng và trang đăng nhập/đổi mật khẩu hiện tại. |
| `js/main.js` | Vị trí dành cho thao tác chung; hiện chưa có xử lý. |
| `js/employees.js` | Tìm kiếm, lọc, phân trang và gửi thông tin biểu mẫu để lưu. |
| `js/dev-login.js` | Tự điền tài khoản/mật khẩu khi chọn vai trò test. |
| `icons/employees/*.svg` | Các file biểu tượng của Hồ sơ/Hợp đồng. |
| `fonts/inter/inter.css`, `fonts/inter/*.ttf` | Khai báo và các file phông chữ Inter. |
| `fonts/inter/OFL.txt` | Giấy phép sử dụng phông chữ. |
| `images/` | Nơi thêm ảnh dùng trong giao diện. |

## 2. Phạm vi và thực thể theo ERD

**Use Case (UC)** là nhóm công việc người dùng thực hiện. **ERD** là sơ đồ các loại dữ liệu và cách chúng liên kết. Đặc tả có **15 thực thể**:

| UC / thư mục | Thực thể | Thông tin được lưu |
| --- | --- | --- |
| UC1 — `accounts` | `NGUOIDUNG` | Tài khoản, mật khẩu, vai trò và trạng thái hoạt động. |
| UC2 — `employees` | `PHONGBAN` | Danh mục phòng ban. |
| UC2 — `employees` | `NHANVIEN` | Hồ sơ, công việc và thông tin nghỉ việc. |
| UC2 — `employees` | `HOPDONG` | Loại hợp đồng, thời hạn, lương và gia hạn. |
| UC3 — `attendance` | `CHAMCONG` | Giờ vào/ra, giờ làm, đi trễ, về sớm, làm thêm. |
| UC3 — `attendance` | `DONNGHIPHEP` | Đơn nghỉ, người gửi/người duyệt và kết quả xét duyệt. |
| UC3 — `attendance` | `LOAIPHEP` | Loại nghỉ, hưởng lương và có trừ phép năm hay không. |
| UC4 — `training` | `DAOTAO` | Khóa đào tạo, nội dung và thời gian học. |
| UC4 — `training` | `NV_DAOTAO` | Nhân viên được phân công học, tiến độ và kết quả. |
| UC5 — `performance` | `KYDANHGIA` | Tên và thời gian kỳ đánh giá. |
| UC5 — `performance` | `TIEUCHI` | Tiêu chí thuộc từng kỳ đánh giá. |
| UC5 — `performance` | `DANHGIA` | Kết quả đánh giá nhân viên theo kỳ. |
| UC5 — `performance` | `CHITIETDANHGIA` | Điểm và nhận xét theo từng tiêu chí. |
| UC5 — `performance` | `KHENTHUONG_KYLUAT` | Quyết định, hình thức và lý do thưởng/phạt. |
| UC5 — `performance` | `PHANHOI` | Ý kiến của nhân viên về kết quả đánh giá. |

Nơi khai báo bảng là `models.py` của thư mục tương ứng. Hiện đã có bốn bảng `NGUOIDUNG`, `PHONGBAN`, `NHANVIEN`, `HOPDONG`; các bảng khác chờ phát triển.

Các phần cùng dùng **một hồ sơ nhân viên**: tài khoản có thể liên kết một hồ sơ; hồ sơ thuộc một phòng ban và có nhiều hợp đồng, ngày công, đơn nghỉ, khóa học, đánh giá. UC3–5 liên kết đến `NHANVIEN` hiện có, không tạo lại bảng nhân viên. Dashboard tổng hợp từ các phần này; `dashboard` và `core` không có thực thể riêng trong ERD.

## 3. Phân công và thứ tự phát triển

### Phạm vi từng thành viên

Trong các thư mục `apps/` được giao, mỗi người phụ trách `models.py`, `forms.py`, `views.py`, `urls.py`, `admin.py`, `tests.py`, `migrations/` theo chức năng giải thích ở mục 1.

| Thành viên | Use Case và công việc | Thư mục xử lý | Thư mục giao diện |
| --- | --- | --- | --- |
| **Hoài Anh** | **UC1:** Tài khoản, phân quyền và Dashboard. Quản trị tài khoản; tổng quan nhân sự, công, phép, hợp đồng và đào tạo. | `apps/accounts/`, `apps/dashboard/` | `templates/accounts/`, `templates/dashboard/` |
| **Hồng Vân** | **UC2:** Hồ sơ và Hợp đồng. Phòng ban, thêm/xem/sửa/vô hiệu hóa hồ sơ, tạo/gia hạn hợp đồng, xem thông tin cá nhân. | `apps/employees/`, gồm `access.py`, `api.py`, `serializers.py` và bộ mẫu | `templates/employees/` |
| **Như** | **UC3:** Chấm công và quản lý phép. Giờ vào/ra, lịch sử/tổng hợp/xuất bảng công, gửi/duyệt/từ chối đơn, quỹ phép. | `apps/attendance/` | `templates/attendance/records/`, `templates/attendance/leave_requests/`, `templates/attendance/leave_balances/` |
| **Nhi** | **UC4:** Đào tạo nội bộ. Khóa học, phân công, xác nhận hoàn thành, theo dõi/cập nhật kết quả. | `apps/training/` | `templates/training/courses/`, `templates/training/assignments/` |
| **Hạ** | **UC5:** Đánh giá và khen thưởng. Kỳ, tiêu chí, điểm, công bố kết quả, phản hồi, thưởng/kỷ luật. | `apps/performance/` | `templates/performance/periods/`, `templates/performance/criteria/`, `templates/performance/evaluations/`, `templates/performance/rewards_discipline/` |

File kiểu dáng/thao tác: Hồng Vân phụ trách `static/css/employees.css`, `static/js/employees.js`; Hoài Anh phụ trách `static/js/dev-login.js` và phối hợp khi sửa kiểu dáng đăng nhập. Các phần mới tạo file riêng như `static/css/attendance.css`, `static/js/attendance.js`; tương tự cho `dashboard`, `training`, `performance`. Các file riêng này **chưa được tạo**.

**Thống nhất trước khi sửa phần dùng chung:** `config/`, `apps/core/`, `templates/base.html`, `templates/includes/`, `static/css/base.css`, `static/js/main.js`, `requirements.txt`, `.env.example`. Cập nhật `README.md` và `docs/` khi thay đổi cách sử dụng. Menu hiện nằm trong `templates/employees/base.html`; phối hợp khi nối các UC khác để thống nhất khung trang và liên kết.

### Thứ tự làm việc

1. **Kiểm tra nền tảng UC1 và UC2:** cả nhóm chạy được đăng nhập, hồ sơ và bộ mẫu. Hoài Anh/Hồng Vân thống nhất liên kết tài khoản với nhân viên và quyền hai vai trò.
2. **Phát triển UC3, UC4, UC5:** Như, Nhi, Hạ có thể làm song song sau khi thống nhất bảng dùng chung. Mỗi UC làm theo thứ tự: thông tin cần lưu → giao diện → xử lý/lưu dữ liệu → kiểm tra quyền và lỗi.
3. **Hoàn thiện Dashboard của UC1:** Hoài Anh lấy số liệu thật, bổ sung chỉ số khi từng phần hoàn thành.
4. **Ghép và kiểm tra toàn dự án:** kiểm tra hai vai trò, menu, dữ liệu liên kết và việc chạy trên máy khác. Thiết lập database chung khi cần thử tích hợp cùng một tập dữ liệu.

Khi thay đổi bảng của phần mình, chạy:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations <ten_thu_muc>
.\.venv\Scripts\python.exe manage.py migrate
```

Thay `<ten_thu_muc>` bằng `attendance`, `training` hoặc tên phần đang làm. Đưa các file mới trong `migrations/` lên repo cùng code. Người nhận code mới chạy `migrate` để cập nhật bảng; giữ các file thay đổi bảng đã có.

## 4. Chạy dự án và nạp dữ liệu trên Windows

Lần đầu làm theo đúng thứ tự. Các lệnh chạy trong **PowerShell tại thư mục chứa `manage.py`**.

### Bước 1 — Chuẩn bị Python và mở thư mục

Cài Python 3.10 trở lên. Kiểm tra:

```powershell
python --version
```

Mở PowerShell tại thư mục dự án, hoặc dùng lệnh dưới đây; thay đường dẫn nếu lưu ở nơi khác:

```powershell
cd "D:\LTW_NHOM9_QLNS_CAKECRUSH"
```

### Bước 2 — Cài thư viện cho dự án

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu đã có `.venv`, bỏ qua lệnh đầu. Từ đây dùng `.\.venv\Scripts\python.exe` để chạy với đúng thư viện; không cần bật môi trường bằng lệnh khác.

### Bước 3 — Tạo file thiết lập riêng

```powershell
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
```

Lệnh chỉ sao chép khi chưa có `.env`. Giữ `DJANGO_DEBUG=True` trong file này để dùng nút đăng nhập nhanh và nạp mẫu trong quá trình phát triển.

### Bước 4 — Kết nối và tạo database

Dự án đã cấu hình **SQLite** trong `config/settings.py`: dữ liệu lưu vào **`db.sqlite3`** trong thư mục dự án. Không cần cài chương trình database riêng hoặc nhập tên máy chủ/mật khẩu kết nối.

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

Lệnh tạo database nếu chưa có, tạo/cập nhật bảng và thêm **6 phòng ban**. Website tự dùng database này mỗi lần chạy. Dữ liệu lưu lại sau khi đóng trình duyệt; bước này chưa nạp hồ sơ/hợp đồng mẫu.

### Bước 5 — Tạo tài khoản test

```powershell
.\.venv\Scripts\python.exe manage.py create_dev_accounts
```

Tạo `dev_manager` và `dev_staff`, mật khẩu riêng trên từng máy lưu ở `.local/dev-login-accounts.json`. Chạy lại giữ nguyên mật khẩu; nút chọn vai trò tự điền thông tin của máy đang chạy.

### Bước 6 — Nạp bộ dữ liệu mẫu

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_data
```

Bộ mẫu có **10 nhân viên ở 6 phòng ban, 11 hợp đồng**. Lệnh liên kết `dev_staff` với **Phạm Thu Hà** nếu tài khoản chưa có hồ sơ. Có các tình huống để thử tìm kiếm, lọc, phân trang, cảnh báo hết hạn và hồ sơ đã nghỉ việc.

File mẫu là `apps/employees/sample_data/hr_demo.json`, ngày tham chiếu **08/10/2026**. Ngày hợp đồng cố định; trạng thái thay đổi theo ngày hiện tại. Chạy lại không tạo trùng hoặc đặt lại dữ liệu đã sửa. Nếu có thông tin trùng/xung đột, lệnh hủy lần nạp để giữ dữ liệu đang có. Chỉ nạp mẫu khi `DJANGO_DEBUG=True`.

UC3–5 chưa có bảng và dữ liệu mẫu. Khi hoàn thiện, người phụ trách bổ sung lệnh nạp mẫu cho phần của mình.

### Bước 7 — Mở website và đăng nhập

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Mở [trang đăng nhập](http://127.0.0.1:8000/accounts/login/), chọn **Quản lý** hoặc **Nhân viên**, rồi bấm **Đăng nhập**. Giữ PowerShell đang chạy; bấm `Ctrl+C` để dừng website.

| Trang | Địa chỉ |
| --- | --- |
| Hồ sơ nhân viên — Quản lý | [Danh sách hồ sơ](http://127.0.0.1:8000/employees/) |
| Hợp đồng — Quản lý | [Danh sách hợp đồng](http://127.0.0.1:8000/employees/contracts/) |
| Hồ sơ cá nhân — Nhân viên | [Hồ sơ của tôi](http://127.0.0.1:8000/employees/me/) |
| Hợp đồng cá nhân — Nhân viên | [Hợp đồng của tôi](http://127.0.0.1:8000/employees/me/contracts/) |
| Quản trị hệ thống | [Django Admin](http://127.0.0.1:8000/admin/) |

Hai tài khoản test không có quyền vào Django Admin. Nếu cần quản lý tài khoản/phòng ban hoặc liên kết hồ sơ tại trang quản trị, chạy **một lần khi chưa có quản trị viên ban đầu**:

```powershell
.\.venv\Scripts\python.exe manage.py create_local_manager
```

Tên quản trị viên là `cakecrush_admin`; mật khẩu ở `.local/local-manager-login.json`. Nếu tài khoản đã có, lệnh báo không tạo lại. Tài khoản này vào được cả website và Django Admin.

**Lần mở sau:** vào thư mục dự án và chạy `runserver`. Sau khi kéo code có thay đổi bảng, chạy `migrate` trước. Nếu `requirements.txt` thay đổi, cài lại thư viện theo bước 2. Không cần tạo lại database, tài khoản hoặc bộ mẫu mỗi lần mở.

## 5. Database khi làm việc nhóm

Mỗi máy hiện có database riêng. Để thành viên khác thấy cùng bộ mẫu ban đầu, đưa **code, các file trong `migrations/`, file mẫu và lệnh nạp** lên repo; người nhận làm theo mục 4.

Việc thêm/sửa trên một máy **không tự cập nhật sang máy khác**. Mã NV/HD có thể khác nếu mỗi máy đã có dữ liệu trước khi nạp mẫu. Tên tài khoản test giống nhau, mật khẩu riêng theo máy.

Không đưa `.env`, `.local/`, `.venv/`, `db.sqlite3` hoặc file người dùng tải lên vào repo; `.gitignore` đã bỏ qua các phần này. Khi cần cập nhật dữ liệu đồng thời, nhóm phải kết nối một database chung trên máy chủ. Dự án hiện chưa thiết lập kết nối chung đó.

## 6. Kiểm tra và tài liệu chi tiết

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test apps.accounts apps.employees
```

Lệnh đầu kiểm tra thiết lập. Lệnh sau kiểm tra đăng nhập, quyền, hồ sơ, hợp đồng và bộ mẫu bằng database kiểm tra riêng. Khi phát triển UC khác, thêm `apps.attendance`, `apps.training` hoặc `apps.performance` vào lệnh `test`.

- [Database và tài khoản](docs/database.md).
- [Cấu trúc và đối chiếu đặc tả](docs/project_structure.md).
- [Thiết kế Hồ sơ và Hợp đồng](https://www.figma.com/design/8V72DiRIlHwmbqjCZf7Ka8/QLHS---QLH%25C4%2590?node-id=0-1).
