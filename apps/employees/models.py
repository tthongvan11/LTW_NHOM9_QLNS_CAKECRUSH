"""Persistent employee records and labor contracts from the specification."""
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models, transaction
from django.db.models.functions import Cast, Lower, Substr
from django.utils import timezone


# Danh mục phòng ban dùng chung; hồ sơ lưu liên kết tới phòng ban thay vì chép tên phòng ban vào từng dòng.
class Department(models.Model):
    id = models.CharField("Mã phòng ban", max_length=10, primary_key=True, db_column="maphongban")
    name = models.CharField("Tên phòng ban", max_length=100, unique=True, db_column="tenphongban")
    description = models.TextField("Mô tả", blank=True, db_column="mota")
    created_at = models.DateTimeField(auto_now_add=True, db_column="ngaytao")

    class Meta:
        db_table = "PHONGBAN"
        ordering = ["name"]
        verbose_name = verbose_name_plural = "Phòng ban"

    def __str__(self):
        return self.name


# Chặn xóa bằng nhóm bản ghi qua Django để giữ lịch sử; thao tác SQL trực tiếp nằm ngoài lớp bảo vệ này.
class HistoryQuerySet(models.QuerySet):
    def delete(self):
        raise ValidationError("Không được xóa hồ sơ hoặc hợp đồng. Cần giữ lịch sử công tác.")


# Phần dùng chung cho mã NV/HD và kiểm tra trước khi lưu; hai bảng con không phải tự viết lại quy trình.
class CodedHistoryModel(models.Model):
    """SQLite IMMEDIATE transactions serialize code allocation and writes."""
    objects = HistoryQuerySet.as_manager()
    code_prefix = ""

    class Meta:
        abstract = True

    # Giao dịch SQLite IMMEDIATE trong settings tuần tự hóa thao tác ghi, bảo vệ bước đọc mã lớn nhất rồi cấp mã mới.
    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Chỉ cấp mã cho bản ghi chưa có mã; sửa một hồ sơ/hợp đồng giữ nguyên mã cũ.
            if not self.pk:
                highest = type(self).objects.filter(pk__startswith=self.code_prefix).aggregate(value=models.Max(Cast(Substr("pk", len(self.code_prefix) + 1), models.IntegerField())))["value"] or 0
                self.pk = f"{self.code_prefix}{highest + 1:03d}"
            # Kiểm tra trường, quy tắc nghiệp vụ và ràng buộc trước khi giao việc ghi thật cho Django.
            self.full_clean()
            return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Không được xóa hồ sơ hoặc hợp đồng. Cần giữ lịch sử công tác.")


# Mỗi hồ sơ thuộc một phòng ban và có thể liên kết một tài khoản; có thể tạo hồ sơ trước khi cấp tài khoản.
class Employee(CodedHistoryModel):
    code_prefix = "NV"
    id = models.CharField("Mã nhân viên", max_length=10, primary_key=True, editable=False, db_column="manv")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="employee", db_column="id_taikhoan", verbose_name="Tài khoản")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees", db_column="maphong", verbose_name="Phòng ban")
    name = models.CharField("Họ và tên", max_length=100, db_column="tennv")
    birth_date = models.DateField("Ngày sinh", null=True, blank=True, db_column="ngaysinh")
    gender = models.CharField("Giới tính", max_length=3, choices=[("Nam", "Nam"), ("Nữ", "Nữ")], db_column="gioitinh")
    phone = models.CharField("Số điện thoại", max_length=10, unique=True, db_column="sdt", validators=[RegexValidator(r"\A0[0-9]{9}\Z", "Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0.")])
    email = models.EmailField("Email", unique=True, db_column="email")
    identity = models.CharField("CCCD", max_length=12, unique=True, db_column="cccd", validators=[RegexValidator(r"\A[0-9]{12}\Z", "CCCD phải gồm đúng 12 chữ số.")])
    address = models.CharField("Địa chỉ", max_length=255, blank=True, db_column="diachi")
    job = models.CharField("Chức vụ", max_length=100, db_column="chucvu")
    start_date = models.DateField("Ngày vào làm", db_column="ngayvaolam")
    is_active = models.BooleanField("Đang làm việc", default=True, db_column="trangthai")
    end_date = models.DateField("Ngày nghỉ việc", null=True, blank=True, db_column="ngaynghiviec")
    reason = models.TextField("Lý do nghỉ việc", blank=True, db_column="lydonghiviec")

    class Meta:
        db_table = "NHANVIEN"
        ordering = ["id"]
        verbose_name = verbose_name_plural = "Nhân viên"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="employee_email_case_insensitive"),
            models.CheckConstraint(condition=models.Q(end_date__isnull=True) | models.Q(end_date__gte=models.F("start_date")), name="employee_end_after_start"),
            models.CheckConstraint(condition=models.Q(is_active=True, end_date__isnull=True, reason="") | (models.Q(is_active=False, end_date__isnull=False) & ~models.Q(reason="")), name="employee_departure_required"),
        ]

    # Chuẩn hóa chữ nhập vào, kiểm tra ngày và tính nhất quán giữa trạng thái làm việc/thông tin nghỉ việc.
    def clean(self):
        errors = {}
        self.name = self.name.strip()
        self.job = self.job.strip()
        self.email = self.email.strip().lower()
        self.reason = self.reason.strip()
        if not self.name:
            errors["name"] = "Vui lòng nhập họ và tên."
        if not self.job:
            errors["job"] = "Vui lòng nhập chức vụ."
        if self.birth_date and self.birth_date >= timezone.localdate():
            errors["birth_date"] = "Ngày sinh phải trước ngày hiện tại."
        if self.birth_date and self.start_date and self.start_date < self.birth_date:
            errors["start_date"] = "Ngày vào làm phải sau ngày sinh."
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["start_date"] = "Ngày vào làm không được sau ngày nghỉ việc."
        if not self.is_active and (not self.end_date or not self.reason):
            errors["__all__"] = "Phải có ngày nghỉ việc và lý do khi vô hiệu hóa hồ sơ."
        if self.is_active and (self.end_date or self.reason):
            errors["__all__"] = "Hồ sơ đang làm việc không được có thông tin nghỉ việc."
        if self.user_id and self.is_active and not self.user.is_active:
            errors["__all__"] = "Tài khoản được liên kết đang bị khóa."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.pk} · {self.name}"


# Mỗi hợp đồng thuộc một nhân viên; ngày và lương được lưu bằng kiểu dữ liệu phù hợp, không chỉ là chữ hiển thị.
class Contract(CodedHistoryModel):
    class Type(models.TextChoices):
        PROBATION = "THU_VIEC", "Thử việc"
        FIXED = "XAC_DINH_1_NAM", "Xác định thời hạn 1 năm"
        INDEFINITE = "KHONG_XAC_DINH", "Không xác định thời hạn"

    class Status(models.TextChoices):
        UPCOMING = "CHUHIEULUC", "Chưa hiệu lực"
        ACTIVE = "DANGHIEULUC", "Đang hiệu lực"
        EXPIRED = "HETHAN", "Hết hạn"
        TERMINATED = "CHAMDUT", "Chấm dứt"

    code_prefix = "HD"
    id = models.CharField("Mã hợp đồng", max_length=10, primary_key=True, editable=False, db_column="mahd")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="contracts", db_column="manv", verbose_name="Nhân viên")
    type = models.CharField("Loại hợp đồng", max_length=30, choices=Type.choices, db_column="loaihd")
    signed_date = models.DateField("Ngày ký", db_column="ngayky")
    start_date = models.DateField("Ngày bắt đầu", db_column="ngaybatdau")
    end_date = models.DateField("Ngày hết hạn", null=True, blank=True, db_column="ngayhethan")
    salary = models.DecimalField("Lương cơ bản", max_digits=18, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], db_column="luongcoban")
    renewal_date = models.DateField("Ngày gia hạn", null=True, blank=True, db_column="ngaygiahan")
    status = models.CharField("Trạng thái", max_length=20, choices=Status.choices, default=Status.UPCOMING, db_column="trangthai")

    class Meta:
        db_table = "HOPDONG"
        ordering = ["id"]
        verbose_name = verbose_name_plural = "Hợp đồng"
        constraints = [
            models.CheckConstraint(condition=models.Q(salary__gte=Decimal("0.01")), name="contract_positive_salary"),
            models.CheckConstraint(condition=models.Q(signed_date__lte=models.F("start_date")), name="contract_sign_before_start"),
            models.CheckConstraint(condition=models.Q(type="KHONG_XAC_DINH", end_date__isnull=True) | (~models.Q(type="KHONG_XAC_DINH") & models.Q(end_date__isnull=False, end_date__gt=models.F("start_date"))), name="contract_valid_end_date"),
        ]

    @property
    # Trạng thái hiệu lực dựa vào ngày máy chủ; Chấm dứt được ưu tiên giữ nguyên nếu đã lưu trạng thái đó.
    def computed_status(self):
        if self.status == self.Status.TERMINATED:
            return self.Status.TERMINATED
        today = timezone.localdate()
        if self.start_date > today:
            return self.Status.UPCOMING
        if self.end_date and self.end_date < today:
            return self.Status.EXPIRED
        return self.Status.ACTIVE

    @property
    # Sắp hết hạn là nhãn hiển thị khi còn 1–30 ngày; đúng ngày hết hạn vẫn là Đang hiệu lực.
    def display_status(self):
        status = self.computed_status
        if status == self.Status.ACTIVE and self.end_date and 0 < (self.end_date - timezone.localdate()).days <= 30:
            return "expiring"
        return {self.Status.UPCOMING: "upcoming", self.Status.ACTIVE: "active", self.Status.EXPIRED: "expired", self.Status.TERMINATED: "terminated"}[status]

    # Kiểm tra nhân viên, loại hợp đồng, các ngày và khoảng thời gian bị trùng với hợp đồng khác.
    def clean(self):
        errors = {}
        if self._state.adding and self.employee_id and not self.employee.is_active:
            errors["__all__"] = "Chỉ được tạo hợp đồng cho nhân viên đang làm việc."
        if self.signed_date and self.start_date and self.signed_date > self.start_date:
            errors["signed_date"] = "Ngày ký không được sau ngày bắt đầu hợp đồng."
        if self.type == self.Type.INDEFINITE and self.end_date:
            errors["end_date"] = "Hợp đồng không xác định thời hạn phải để trống ngày hết hạn."
        if self.type != self.Type.INDEFINITE and (not self.end_date or (self.start_date and self.end_date <= self.start_date)):
            errors["end_date"] = "Ngày hết hạn phải sau ngày bắt đầu."
        if self.renewal_date and self.start_date and (self.renewal_date < self.start_date or (self.end_date and self.renewal_date > self.end_date)):
            errors["renewal_date"] = "Ngày gia hạn phải nằm trong thời gian hiệu lực của hợp đồng."
        if self.employee_id and self.start_date and not errors:
            # Hai khoảng trùng khi hợp đồng cũ kết thúc từ ngày mới bắt đầu và bắt đầu trước/khi ngày mới kết thúc.
            overlapping = Contract.objects.filter(employee_id=self.employee_id).exclude(pk=self.pk).exclude(status=self.Status.TERMINATED).filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=self.start_date))
            if self.end_date:
                overlapping = overlapping.filter(start_date__lte=self.end_date)
            if overlapping.exists():
                errors["__all__"] = "Khoảng thời gian này trùng với một hợp đồng khác của nhân viên."
        if errors:
            raise ValidationError(errors)

    # Lần lưu cập nhật trạng thái trong bảng; lúc xem vẫn tính lại để không phụ thuộc một tác vụ chạy hằng ngày.
    def save(self, *args, **kwargs):
        if self.start_date:
            self.status = self.computed_status
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pk} · {self.employee.name}"
