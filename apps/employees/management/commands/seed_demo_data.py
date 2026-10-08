"""Load reproducible development HR samples without replacing existing records."""
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from apps.employees.models import Contract, Department, Employee


SAMPLE_PATH = Path(__file__).resolve().parents[2] / "sample_data" / "hr_demo.json"


class Command(BaseCommand):
    help = "Nạp hồ sơ/hợp đồng mẫu cho dev; giữ nguyên bản ghi đã có."

    # Lệnh riêng cho dev: đọc file mẫu và thêm bản ghi còn thiếu; không dùng dữ liệu mẫu như dữ liệu nhân sự thật.
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Sample data can only be loaded in development (DEBUG=True).")
        try:
            data = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise CommandError("Cannot read the development sample dataset.") from error
        employees_created = contracts_created = 0
        linked_staff = False
        try:
            # Nếu một mẫu không hợp lệ thì hủy cả lần nạp để không để lại bộ dữ liệu mới chỉ được thêm một phần.
            with transaction.atomic():
                employees = {}
                newly_created = {}
                for entry in data["employees"]:
                    email = entry["email"].lower()
                    employee = Employee.objects.filter(email__iexact=email).first()
                    if employee is None:
                        department = Department.objects.get(pk=entry["department"])
                        fields = {key: entry[key] for key in ("name", "job", "gender", "phone", "identity", "address")}
                        employee = Employee.objects.create(
                            email=email, department=department,
                            birth_date=date.fromisoformat(entry["birth_date"]),
                            start_date=date.fromisoformat(entry["start_date"]), **fields,
                        )
                        newly_created[email] = entry
                        employees_created += 1
                    employees[email] = employee

                for entry in data["contracts"]:
                    employee = employees[entry["employee_email"]]
                    # These fields are immutable through the UI. Edited salary/end
                    # dates stay intact, and reruns on later days do not duplicate data.
                    # Nhận diện hợp đồng bằng các trường gốc bất biến; ngày/lương đã sửa sẽ được giữ khi chạy lại.
                    lookup = {"employee": employee, "type": entry["type"],
                              "signed_date": date.fromisoformat(entry["signed_date"]),
                              "start_date": date.fromisoformat(entry["start_date"])}
                    if not Contract.objects.filter(**lookup).exists():
                        Contract.objects.create(
                            **lookup,
                            end_date=date.fromisoformat(entry["end_date"]) if entry.get("end_date") else None,
                            renewal_date=date.fromisoformat(entry["renewal_date"]) if entry.get("renewal_date") else None,
                            salary=Decimal(entry["salary"]),
                            status=entry.get("status", Contract.Status.UPCOMING),
                        )
                        contracts_created += 1

                # Create historical contracts while the new employee is active,
                # then apply the departure state to these newly added samples only.
                for email, entry in newly_created.items():
                    if entry.get("end_date"):
                        employee = employees[email]
                        employee.is_active = False
                        employee.end_date = date.fromisoformat(entry["end_date"])
                        employee.reason = entry["reason"]
                        employee.save(update_fields=["is_active", "end_date", "reason"])

                # Chỉ liên kết dev_staff khi cả tài khoản và hồ sơ chưa có liên kết khác, tránh thay hồ sơ đang dùng.
                staff = get_user_model().objects.filter(username="dev_staff", role="STAFF", is_active=True, is_superuser=False).first()
                employee = employees[data["staff_employee_email"]]
                if staff and employee.is_active and not employee.user_id and not Employee.objects.filter(user=staff).exists():
                    employee.user = staff
                    employee.save(update_fields=["user"])
                    linked_staff = True
        except (ValidationError, IntegrityError, Department.DoesNotExist, KeyError, ValueError) as error:
            raise CommandError(f"Sample import cancelled; no HR records were changed. Check migrations and conflicting sample fields. Details: {error}") from error

        self.stdout.write(self.style.SUCCESS(f"Added {employees_created} employees and {contracts_created} contracts. Existing records preserved."))
        if linked_staff:
            self.stdout.write("Linked dev_staff to Pham Thu Ha's sample profile and contract.")
        elif staff is None:
            self.stdout.write("Run create_dev_accounts and seed_demo_data to enable the staff login sample.")
