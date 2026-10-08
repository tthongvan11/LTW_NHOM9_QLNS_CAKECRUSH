# Báo cáo phân tích Hồ sơ và Hợp đồng — 08/10/2026

Đã tạo tài liệu Word gồm **12 chương**, **124 trang**, mục lục đã cập nhật, số trang, **12 sơ đồ** và trích đoạn mã thật. Nội dung dành cho người mới: theo từng thao tác, đầu vào/kết quả, chuỗi hàm, quy tắc, ví dụ giả định và điều xảy ra nếu bỏ phần xử lý. Nội dung chính Times New Roman 13; đoạn mã Consolas 9.

Tài liệu: [Giai_thich_Module_Quan_ly_Ho_so_va_Hop_dong_Lao_dong.docx](../Giai_thich_Module_Quan_ly_Ho_so_va_Hop_dong_Lao_dong.docx).

## Phạm vi đã phân tích

- Đọc/lọc/phân trang/chi tiết hồ sơ; thêm/sửa; vô hiệu hóa và khóa tài khoản liên kết.
- Đọc/lọc/chi tiết hợp đồng; tạo mới; cập nhật/gia hạn; kiểm khoảng trùng; tính nhãn hiệu lực và cảnh báo hết hạn.
- Trang hồ sơ/hợp đồng cá nhân; xác thực và quyền; CSRF; lỗi; dữ liệu bootstrap; template/CSS/JavaScript.
- Model và quan hệ NGUOIDUNG, PHONGBAN, NHANVIEN, HOPDONG; cấp mã; giữ lịch sử; admin; cấu hình SQLite; migrations; nạp mẫu và tài khoản test.
- Mô phỏng bằng dữ liệu giả định, không ghi ví dụ vào database đang dùng. Chương 7 có 10 nhóm luồng; chương 9 nối các bước trong một tình huống.

## Source đã đọc/đối chiếu

Các file dưới đây có trong bảng nguồn dùng để tạo tài liệu; số dòng là phiên bản sau comment. Các phần tài khoản và cấu hình chỉ phân tích ở mức cần cho module.

| File | Số dòng |
|---|---:|
| `apps/employees/access.py` | 23 |
| `apps/employees/views.py` | 98 |
| `apps/employees/api.py` | 103 |
| `apps/employees/forms.py` | 65 |
| `apps/employees/models.py` | 200 |
| `apps/employees/serializers.py` | 49 |
| `apps/employees/urls.py` | 24 |
| `apps/employees/admin.py` | 33 |
| `apps/employees/management/commands/seed_demo_data.py` | 94 |
| `apps/accounts/models.py` | 22 |
| `apps/accounts/views.py` | 21 |
| `apps/accounts/dev_login.py` | 39 |
| `config/settings.py` | 112 |
| `config/urls.py` | 19 |
| `static/js/employees.js` | 471 |
| `static/js/dev-login.js` | 26 |
| `static/css/employees.css` | 387 |
| `templates/employees/base.html` | 72 |
| `templates/employees/employees/list.html` | 15 |
| `templates/employees/employees/form.html` | 25 |
| `templates/employees/employees/detail.html` | 6 |
| `templates/employees/employees/my_profile.html` | 5 |
| `templates/employees/contracts/list.html` | 15 |
| `templates/employees/contracts/form.html` | 8 |
| `templates/employees/contracts/detail.html` | 6 |
| `templates/employees/contracts/my_contracts.html` | 5 |
| `templates/employees/includes/icon.html` | 1 |
| `templates/accounts/login.html` | 33 |
| `apps/employees/tests.py` | 303 |
| `apps/accounts/tests.py` | 112 |
| `apps/accounts/urls.py` | 11 |
| `apps/accounts/management/commands/create_dev_accounts.py` | 38 |
| `templates/base.html` | 22 |
| `apps/employees/apps.py` | 7 |
| `apps/employees/migrations/0001_initial.py` | 105 |
| `apps/employees/migrations/0002_departments.py` | 12 |
| `apps/employees/migrations/0003_remove_contract_contract_valid_end_date_and_more.py` | 21 |
| `apps/employees/sample_data/hr_demo.json` | 31 |

Các thư mục khung dashboard, attendance, training, performance và điều hướng chung được khảo sát để xác nhận chưa có liên kết nghiệp vụ từ chức năng hiện tại. Không giả định các chức năng tương lai đã hoạt động.

## Comment đã bổ sung

**113 comment / 28 file. Chỉ thêm comment, không đổi logic.** Không sửa tests, migrations, JSON, requirements hay schema. Dữ liệu và README thay đổi từ các lượt trước được giữ nguyên.

| File | Dòng comment sau sửa | Số comment |
|---|---|---:|
| `apps/employees/access.py` | 8, 13 | 2 |
| `apps/employees/views.py` | 11, 22, 28, 34, 44, 56, 62, 68, 74, 84, 96 | 11 |
| `apps/employees/api.py` | 18, 30, 38, 43, 52, 63, 70, 75, 85, 94 | 10 |
| `apps/employees/forms.py` | 7, 15, 23, 32, 36, 44, 51, 60 | 8 |
| `apps/employees/models.py` | 11, 27, 33, 42, 45, 49, 57, 86, 116, 151, 163, 170, 184, 193 | 14 |
| `apps/employees/serializers.py` | 5, 10, 20, 28, 32, 36, 47 | 7 |
| `apps/employees/urls.py` | 7 | 1 |
| `apps/employees/admin.py` | 6, 13, 25 | 3 |
| `apps/employees/management/commands/seed_demo_data.py` | 22, 33, 56, 80 | 4 |
| `apps/accounts/models.py` | 6 | 1 |
| `apps/accounts/views.py` | 7, 12, 18 | 3 |
| `apps/accounts/dev_login.py` | 19, 36 | 2 |
| `config/settings.py` | 44, 74, 83 | 3 |
| `config/urls.py` | 14 | 1 |
| `static/js/employees.js` | 6, 16, 19, 21, 32, 42, 48, 55, 60, 100, 152, 181, 190, 197, 224, 239, 259, 273, 304, 338, 386, 401, 420, 434, 457 | 25 |
| `static/js/dev-login.js` | 2, 15 | 2 |
| `static/css/employees.css` | 1, 98, 234 | 3 |
| `templates/employees/base.html` | 9, 55, 70 | 3 |
| `templates/employees/employees/list.html` | 3 | 1 |
| `templates/employees/employees/form.html` | 5 | 1 |
| `templates/employees/employees/detail.html` | 5 | 1 |
| `templates/employees/employees/my_profile.html` | 4 | 1 |
| `templates/employees/contracts/list.html` | 10 | 1 |
| `templates/employees/contracts/form.html` | 5 | 1 |
| `templates/employees/contracts/detail.html` | 5 | 1 |
| `templates/employees/contracts/my_contracts.html` | 4 | 1 |
| `templates/employees/includes/icon.html` | 1 | 1 |
| `templates/accounts/login.html` | 11 | 1 |

[doi_chieu_comment.json](doi_chieu_comment.json) ghi toàn bộ nội dung/vị trí comment, dấu kiểm SHA-256 trước/sau và kết quả đối chiếu. Chương 11 Word còn ghi phần code được giải thích và lý do.

Có 697 lượt dẫn chứng được kiểm tra tự động: [dan_chieu_ma_nguon.json](dan_chieu_ma_nguon.json). Các lượt có thể trùng vì một hàm tham gia nhiều thao tác; đây không phải số hàm khác nhau.

## Sơ đồ bàn giao

Mỗi sơ đồ có PNG được nhúng trong Word và SVG có thể chỉnh sửa. [tao_so_do.py](tao_so_do.py) là mã tái tạo riêng cho tài liệu; không thuộc đường chạy ứng dụng.

| Sơ đồ | Nội dung |
|---|---|
| [01_kien_truc.png](so_do/01_kien_truc.png) · [SVG](so_do/01_kien_truc.svg) | Kiến trúc |
| [02_quan_he_du_lieu.png](so_do/02_quan_he_du_lieu.png) · [SVG](so_do/02_quan_he_du_lieu.svg) | Quan hệ bốn bảng |
| [03_xem_trang.png](so_do/03_xem_trang.png) · [SVG](so_do/03_xem_trang.svg) | Xem trang |
| [04_luu_ho_so.png](so_do/04_luu_ho_so.png) · [SVG](so_do/04_luu_ho_so.svg) | Lưu hồ sơ |
| [05_vo_hieu_hoa.png](so_do/05_vo_hieu_hoa.png) · [SVG](so_do/05_vo_hieu_hoa.svg) | Vô hiệu hóa |
| [06_luu_hop_dong.png](so_do/06_luu_hop_dong.png) · [SVG](so_do/06_luu_hop_dong.svg) | Lưu hợp đồng |
| [07_tim_kiem.png](so_do/07_tim_kiem.png) · [SVG](so_do/07_tim_kiem.svg) | Tìm/lọc/phân trang |
| [08_ca_nhan.png](so_do/08_ca_nhan.png) · [SVG](so_do/08_ca_nhan.svg) | Trang cá nhân |
| [09_tinh_trang_thai.png](so_do/09_tinh_trang_thai.png) · [SVG](so_do/09_tinh_trang_thai.svg) | Quyết định trạng thái |
| [10_nap_mau.png](so_do/10_nap_mau.png) · [SVG](so_do/10_nap_mau.svg) | Nạp mẫu |
| [11_tuong_tac_luu.png](so_do/11_tuong_tac_luu.png) · [SVG](so_do/11_tuong_tac_luu.svg) | Tương tác khi lưu |
| [12_lien_ket_module.png](so_do/12_lien_ket_module.png) · [SVG](so_do/12_lien_ket_module.svg) | Liên kết module |

## Kiểm tra đã chạy

- Trước comment: `manage.py test apps.accounts apps.employees --verbosity 1` — **28/28 đạt**, 21.388 giây.
- Sau comment: cùng nhóm kiểm thử — **28/28 đạt**, 33.730 giây. Test tạo database thử riêng. Log PermissionDenied là ca kiểm quyền cố ý bị từ chối, không phải lỗi test.
- `manage.py check` — không vấn đề; `manage.py makemigrations --check --dry-run` — không có thay đổi model/schema.
- Python compile và so cấu trúc AST các file sửa — đạt. AST là cấu trúc câu lệnh Python hiểu; comment không nằm trong cấu trúc thực thi này.
- Node `--check` cho employees.js và dev-login.js — đạt.
- Bỏ đúng comment mới: **28/28 file giống byte bản gốc**. Đây cũng bảo vệ các file JS/CSS/template; template dùng comment nội bộ Django nên không thêm chữ/không đổi khoảng trắng trả ra.
- Git status/diff được kiểm tra. Source phần lớn đã untracked trước nhiệm vụ; vì vậy dùng bản gốc và unified diff riêng trong `.local/module-documentation-20261008/` để đối chiếu, không dựa riêng vào git diff.
- Source hash còn đúng sau tạo tài liệu; mọi dẫn chứng ở đúng file/dòng sau comment; 12 heading chương và 12 hình nhúng được kiểm tra.
- Mục lục và trường trang được cập nhật bằng Microsoft Word. Word mở/xuất thành công; đã xem **tất cả 124 ảnh trang ở kích thước gốc 96 DPI**, kiểm bảng, code, sơ đồ, chữ Việt và số trang; không có ký tự ra ngoài vùng trang theo kiểm tra tọa độ PDF. Ảnh/PDF chỉ lưu trong `.local` phục vụ QA.

Công cụ render_docx.py đã được thử, nhưng môi trường không có soffice.exe. Sau khi đọc lỗi, dùng Microsoft Word đang cài để xuất PDF và pypdfium2 tạo ảnh trang. Không cài thêm thư viện hoặc thay dependencies của web.

## Các điểm chưa hoàn thiện và giới hạn

- Có trạng thái Chấm dứt nhưng chưa có thao tác chấm dứt hợp đồng riêng.
- Gia hạn sửa cùng bản ghi; chưa có phiên bản lịch sử/phụ lục/tệp ký hoặc xuất hợp đồng.
- Chưa buộc loại “1 năm” đúng một năm, chưa so ngày bắt đầu HD với ngày vào làm.
- Vô hiệu hóa không tự chấm dứt HD. “Hợp đồng hiện tại” có fallback; trang cá nhân chọn bản có ngày bắt đầu mới nhất, có thể chưa hiệu lực.
- Chính sách “Chưa cập nhật”; chuông thông báo là câu cố định; các module khác ở sidebar chưa hoạt động.
- Tải toàn bộ dữ liệu được phép rồi phân trang 4 dòng ở trình duyệt; chưa realtime, chưa kiểm tập lớn.
- Chưa kiểm nhiều tiến trình ghi đồng thời, ghi đè từ màn hình cũ, độ chính xác số lớn của SQLite, nhiều trình duyệt/thiết bị hoặc triển khai thực tế. select_for_update không được diễn giải như khóa từng hàng trên SQLite.
- Queryset.update/SQL trực tiếp có thể bỏ qua clean/save; admin cho sửa HD rộng hơn API; trạng thái cột lưu và nhãn tính khi đọc có thể khác theo ngày.
- Nhiệm vụ chỉ thêm comment nên không sửa các điểm trên. Không chạy lại mọi nút qua trình duyệt; mô phỏng văn bản và kiểm thử tự động được phân biệt trong Word.
