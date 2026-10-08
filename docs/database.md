# Database cho hồ sơ và hợp đồng Cake Crush

Ứng dụng dùng SQLite tại `db.sqlite3`. Đây là database thật của Django: hồ sơ và hợp đồng được lưu bằng ORM, được đọc lại mỗi lần mở trang và không phụ thuộc bộ nhớ của tab trình duyệt. Database khởi tạo với sáu phòng ban; danh sách nhân viên và hợp đồng để trống để nhập dữ liệu thực tế.

## Các bảng đã triển khai

| Bảng | Model | Quan hệ và chức năng |
| --- | --- | --- |
| NGUOIDUNG | `accounts.User` | Đăng nhập, mật khẩu được băm, vai trò MANAGER/STAFF, trạng thái tài khoản |
| PHONGBAN | `employees.Department` | Danh mục phòng ban; khóa ngoại từ nhân viên |
| NHANVIEN | `employees.Employee` | Hồ sơ; liên kết tùy chọn 1–1 với tài khoản; CCCD, email và điện thoại duy nhất |
| HOPDONG | `employees.Contract` | Nhiều hợp đồng theo từng nhân viên; các ngày hiệu lực, lương Decimal và ngày gia hạn |

Tên bảng và cột nghiệp vụ theo đặc tả. Thuộc tính Python dùng tên tiếng Anh; ví dụ `Employee.name` lưu vào cột `tennv`, `Employee.department` vào `maphong`, `Contract.employee` vào `manv`. Mã NV/HD được sinh khi lưu, không cho sửa qua giao diện. Giao dịch SQLite IMMEDIATE bảo vệ việc cấp mã và các thay đổi đồng thời.

## Bắt đầu sử dụng

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py create_local_manager
.\.venv\Scripts\python.exe manage.py runserver
```

Lệnh tạo quản lý chỉ dùng khi chưa có tài khoản ban đầu, không đặt lại mật khẩu của tài khoản đã tồn tại. Thông tin đăng nhập được sinh riêng và lưu tại `.local/local-manager-login.json`, không đưa vào Git. Đăng nhập tại `http://127.0.0.1:8000/accounts/login/` rồi thêm hồ sơ, tạo hợp đồng. Có thể đổi mật khẩu ở trang Hồ sơ của tôi.

Trong menu tài khoản của quản trị viên, chọn **Quản trị hệ thống** để quản lý phòng ban, tạo tài khoản nhân viên và liên kết tài khoản trong mục **Nhân viên → Tài khoản**. Hồ sơ có thể được tạo trước khi cấp tài khoản, đúng đặc tả. Tài khoản STAFF chỉ xem hồ sơ và hợp đồng đã liên kết với chính mình. Tài khoản chưa liên kết hiển thị thông báo chưa có hồ sơ.

## Chọn vai trò để test nhanh trong môi trường dev

```powershell
.\.venv\Scripts\python.exe manage.py create_dev_accounts
```

Lệnh tạo riêng `dev_manager` (MANAGER) và `dev_staff` (STAFF), với mật khẩu sinh ngẫu nhiên lưu trong `.local/dev-login-accounts.json`, được Git bỏ qua. Chạy lại lệnh sẽ giữ nguyên tài khoản và mật khẩu. Lệnh không tạo hồ sơ nhân viên hoặc hợp đồng mẫu và không thay đổi quản trị viên hiện có.

Khi `DEBUG=True`, trang đăng nhập có nút **Quản lý** và **Nhân viên** để tự điền thông tin, sau đó bấm **Đăng nhập**. Đây là đăng nhập thật qua Django; quyền vẫn lấy từ tài khoản trong database. Nếu mật khẩu đã đổi hoặc tài khoản bị khóa, nút tương ứng không hiển thị. Khi `DEBUG=False`, trang không xuất thông tin test hoặc script tự điền và lệnh tạo tài khoản test bị chặn.

Có thể chạy `seed_demo_data` bên dưới để tự liên kết `dev_staff` với hồ sơ mẫu Phạm Thu Hà. Với hồ sơ tự nhập, dùng quản trị viên liên kết tài khoản qua Django Admin. Nếu chưa liên kết, vai trò Nhân viên sẽ hiển thị trạng thái chưa có hồ sơ.

## Dữ liệu mẫu dùng chung trong repo

Bộ mẫu được lưu tại `apps/employees/sample_data/hr_demo.json`. Đây là dữ liệu giả lập, gồm 10 nhân viên ở đủ 6 phòng ban và 11 hợp đồng: thử việc, xác định thời hạn, không xác định thời hạn, lịch sử hợp đồng và hồ sơ đã nghỉ việc. Ngày tham chiếu của bộ mẫu là **08/10/2026**; vào ngày này giao diện có các trạng thái đang hiệu lực, sắp hết hạn, hết hạn, chưa hiệu lực và chấm dứt. Ngày hợp đồng cố định để các máy nhận cùng dữ liệu; trạng thái vẫn thay đổi theo ngày máy chủ.

Mỗi thành viên kéo code mới, cài thư viện nếu cần, rồi chạy tại thư mục dự án:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py create_dev_accounts
.\.venv\Scripts\python.exe manage.py seed_demo_data
.\.venv\Scripts\python.exe manage.py runserver
```

Trang đăng nhập dev tự điền mật khẩu được sinh riêng trên từng máy. Vai trò Nhân viên xem hồ sơ và hợp đồng của Phạm Thu Hà. Nếu `dev_staff` đã liên kết một hồ sơ khác, lệnh giữ nguyên liên kết đó.

Lệnh chỉ chạy khi `DEBUG=True`. Chạy lại không thêm trùng và không đặt lại tên, lương hoặc dữ liệu đã sửa. Hồ sơ được nhận diện theo email mẫu; hợp đồng theo nhân viên, loại, ngày ký và ngày bắt đầu. Nếu dữ liệu đang có xung đột điện thoại/CCCD hoặc hợp đồng, toàn bộ lần nạp bị hủy để giữ dữ liệu hiện tại. Không dùng lệnh này để phục hồi dữ liệu sau khi sửa các trường nhận diện.

Đưa file JSON, lệnh nạp và tài liệu hướng dẫn lên repo để thành viên khác nhận bộ mẫu. Không đưa `db.sqlite3` hoặc `.local/` lên Git. Mã NV/HD được cấp theo dữ liệu có sẵn trên mỗi máy nên có thể khác nếu database không trống. **Đây là cùng bộ dữ liệu ban đầu trên các database riêng; thay đổi trên một máy không tự đồng bộ sang máy khác.**

## Lưu và kiểm tra dữ liệu

- Các trang được Django cấp dữ liệu qua `json_script` theo phạm vi tài khoản đăng nhập; giao diện giữ tìm kiếm, lọc và phân trang hiện tại.
- Các biểu mẫu gọi POST tại `/employees/api/employees/` và `/employees/api/contracts/`, có CSRF. Sửa/vô hiệu hóa dùng đường dẫn có mã bản ghi.
- Django kiểm tra trường bắt buộc, định dạng, thông tin trùng, ngày sinh, ngày làm việc, ngày ký/hiệu lực/gia hạn, số thập phân và hợp đồng trùng thời gian trước khi lưu.
- Vô hiệu hóa cập nhật ngày và lý do nghỉ việc, khóa tài khoản liên kết, giữ hồ sơ và hợp đồng. Không có chức năng xóa cứng hồ sơ/hợp đồng trên giao diện hay Admin.
- Trạng thái hiển thị tính theo ngày của máy chủ mỗi lần đọc; cảnh báo hết hạn áp dụng khi còn 1–30 ngày. Trường trạng thái lưu trong bảng được tính lại khi lưu hợp đồng; không cần tác vụ hẹn giờ để cảnh báo trên giao diện chính xác.
- Chính sách bổ sung chưa có thuộc tính trong bảng đặc tả được hiển thị “Chưa cập nhật”; không dùng các giá trị minh họa cũ làm dữ liệu doanh nghiệp.

Các dữ liệu demo và thay đổi tạm ở phiên giao diện trước không tự nhập vào database. Dữ liệu mới chỉ xuất hiện sau khi lưu thành công qua Django.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe manage.py test apps.employees apps.accounts
```

Kiểm thử tự tạo database riêng, bao gồm lưu/đọc qua phiên khác, xác thực, CSRF, phân quyền, thông tin trùng, hợp đồng, vô hiệu hóa và giữ lịch sử. Có thể đặt `CAKECRUSH_DATABASE_PATH` tới một tệp SQLite riêng khi kiểm tra bằng trình duyệt; mặc định vẫn dùng `db.sqlite3`. Thư mục `.local/` chứa bản sao lưu trước khi triển khai và database kiểm thử cục bộ.

Các bảng nghiệp vụ chấm công, nghỉ phép, đào tạo và đánh giá vẫn thuộc những phân hệ sẽ phát triển sau.
