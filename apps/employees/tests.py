import json
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Contract, Department, Employee
from io import StringIO
from datetime import date


@override_settings(DEBUG=True)
class DemoDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(username="dev_staff", password="Staff-Sample-938!", role="STAFF")

    def seed(self):
        with patch("apps.employees.models.timezone.localdate", return_value=date(2026, 10, 8)):
            call_command("seed_demo_data", stdout=StringIO())

    def test_samples_cover_departments_statuses_and_staff_profile(self):
        self.seed()
        self.assertEqual(Employee.objects.count(), 10)
        self.assertEqual(Contract.objects.count(), 11)
        self.assertEqual(Employee.objects.filter(is_active=False).count(), 1)
        self.assertEqual(Employee.objects.values("department").distinct().count(), 6)
        own = Employee.objects.get(user=self.staff)
        self.assertEqual(own.email, "demo04@cakecrush.example")
        self.assertEqual(own.contracts.count(), 1)
        with patch("apps.employees.models.timezone.localdate", return_value=date(2026, 10, 8)):
            self.assertEqual({item.display_status for item in Contract.objects.all()}, {"active", "expiring", "expired", "upcoming", "terminated"})
            for item in Employee.objects.all():
                item.full_clean()
            for item in Contract.objects.all():
                item.full_clean()
        self.client.force_login(self.staff)
        response = self.client.get(reverse("employees:my_profile"))
        self.assertEqual(len(response.context["bootstrap"]["employees"]), 1)
        self.assertEqual(len(response.context["bootstrap"]["contracts"]), 1)
        self.assertEqual(response.context["bootstrap"]["currentUser"]["name"], "Phạm Thu Hà")

    def test_rerun_preserves_edits_and_does_not_duplicate_on_another_day(self):
        self.seed()
        employee = Employee.objects.get(email="demo01@cakecrush.example")
        employee.name = "Tên đã sửa khi test"
        employee.save(update_fields=["name"])
        contract = employee.contracts.order_by("start_date").last()
        contract.salary = Decimal("17500000.50")
        contract.save(update_fields=["salary"])
        with patch("apps.employees.models.timezone.localdate", return_value=date(2026, 11, 8)):
            call_command("seed_demo_data", stdout=StringIO())
        employee.refresh_from_db()
        contract.refresh_from_db()
        self.assertEqual(employee.name, "Tên đã sửa khi test")
        self.assertEqual(contract.salary, Decimal("17500000.50"))
        self.assertEqual(Employee.objects.count(), 10)
        self.assertEqual(Contract.objects.count(), 11)

    def test_conflicting_unique_field_rolls_back_the_whole_import(self):
        original = Employee.objects.create(name="Hồ sơ đang có", department=Department.objects.get(pk="BEP"), job="Thợ bánh", gender="Nam", phone="0900000102", identity="000000001999", email="original@example.test", start_date=date(2020, 1, 1))
        with self.assertRaises(CommandError):
            self.seed()
        self.assertEqual(list(Employee.objects.values_list("pk", flat=True)), [original.pk])
        self.assertEqual(Contract.objects.count(), 0)
        self.assertFalse(Employee.objects.filter(user=self.staff).exists())

    def test_existing_staff_link_is_preserved(self):
        original = Employee.objects.create(name="Hồ sơ đang có", department=Department.objects.get(pk="BEP"), job="Thợ bánh", gender="Nam", phone="0900001999", identity="000000001999", email="original@example.test", start_date=date(2020, 1, 1), user=self.staff)
        self.seed()
        self.assertEqual(Employee.objects.get(user=self.staff).pk, original.pk)
        self.assertIsNone(Employee.objects.get(email="demo04@cakecrush.example").user_id)

    def test_production_does_not_load_sample_data(self):
        with override_settings(DEBUG=False), self.assertRaises(CommandError):
            call_command("seed_demo_data", stdout=StringIO())
        self.assertEqual(Employee.objects.count(), 0)
        self.assertEqual(Contract.objects.count(), 0)


class DatabaseWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.manager = User.objects.create_user(username="manager", password="Manager-Test-938!", role="MANAGER")
        cls.staff = User.objects.create_user(username="staff", password="Staff-Test-938!", role="STAFF")
        cls.department = Department.objects.get(pk="BEP")

    def setUp(self):
        self.client.force_login(self.manager)

    def employee_input(self, number=1):
        return {"name": f"Nhân viên kiểm thử {number}", "birth_date": "1998-01-01", "gender": "Nữ", "identity": f"{number:012d}", "phone": f"090{number:07d}", "email": f"employee{number}@example.test", "address": "Địa chỉ kiểm thử", "department": self.department.name, "job": "Thợ bánh", "start_date": "2020-01-01"}

    def post(self, path, data, client=None):
        return (client or self.client).post(path, json.dumps(data), content_type="application/json")

    def create_employee(self, number=1, user=None):
        response = self.post(reverse("employees:employee_save"), self.employee_input(number))
        self.assertEqual(response.status_code, 200, response.content)
        item = Employee.objects.get(pk=response.json()["id"])
        if user:
            item.user = user
            item.save()
        return item

    def contract_input(self, employee, start=None, end=None):
        start = start or timezone.localdate() - timedelta(days=30)
        end = end or timezone.localdate() + timedelta(days=15)
        return {"employee_id": employee.pk, "type": "Xác định thời hạn 1 năm", "signed_date": start.isoformat(), "start_date": start.isoformat(), "end_date": end.isoformat(), "salary": "8500000.25"}

    def create_contract(self, employee, **kwargs):
        response = self.post(reverse("employees:contract_save"), self.contract_input(employee, **kwargs))
        self.assertEqual(response.status_code, 200, response.content)
        return Contract.objects.get(pk=response.json()["id"])

    def test_database_starts_without_demo_personnel(self):
        self.assertEqual(Department.objects.count(), 6)
        self.assertEqual(Employee.objects.count(), 0)
        self.assertEqual(Contract.objects.count(), 0)
        response = self.client.get(reverse("employees:employee_list"))
        self.assertEqual(response.context["bootstrap"]["employees"], [])
        self.assertNotContains(response, "employees-data.js")

    def test_create_and_update_survive_a_different_session(self):
        item = self.create_employee()
        self.assertEqual(item.pk, "NV001")
        data = self.employee_input()
        data.update(name="Tên đã cập nhật", id="FORGED", is_active="false")
        response = self.post(reverse("employees:employee_update", args=[item.pk]), data)
        self.assertEqual(response.status_code, 200, response.content)
        item.refresh_from_db()
        self.assertEqual(item.name, "Tên đã cập nhật")
        self.assertTrue(item.is_active)
        other_session = Client()
        other_session.force_login(self.manager)
        response = other_session.get(reverse("employees:employee_list"))
        self.assertEqual(response.context["bootstrap"]["employees"][0]["name"], item.name)
        self.assertEqual(Contract.objects.count(), 0)

    def test_duplicates_and_invalid_employee_fields_are_rejected(self):
        self.create_employee()
        invalid = [
            {"email": "EMPLOYEE1@EXAMPLE.TEST"}, {"identity": "000000000001"},
            {"phone": "0900000001"}, {"identity": "123"}, {"phone": "123"},
            {"gender": "Khác"}, {"name": "   "}, {"email": "invalid"},
            {"birth_date": (timezone.localdate() + timedelta(days=1)).isoformat()},
            {"start_date": "1990-01-01"}, {"department": "Phòng ban không tồn tại"},
        ]
        for change in invalid:
            with self.subTest(change=change):
                data = self.employee_input(2)
                data.update(change)
                response = self.post(reverse("employees:employee_save"), data)
                self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(Employee.objects.count(), 1)

    def test_employee_codes_do_not_collide_at_three_digit_boundary(self):
        item = self.create_employee()
        Employee.objects.filter(pk=item.pk).update(id="NV999")
        self.assertEqual(self.create_employee(2).pk, "NV1000")
        self.assertEqual(self.create_employee(3).pk, "NV1001")

    def test_contract_create_renew_and_expiry_warning(self):
        employee = self.create_employee()
        contract = self.create_contract(employee)
        self.assertEqual(contract.pk, "HD001")
        self.assertEqual(contract.salary, Decimal("8500000.25"))
        self.assertEqual(contract.display_status, "expiring")
        response = self.post(reverse("employees:contract_update", args=[contract.pk]), {"renewal_date": timezone.localdate().isoformat(), "end_date": (timezone.localdate() + timedelta(days=400)).isoformat(), "salary": "9000000.50", "employee_id": "FORGED", "type": "Thử việc"})
        self.assertEqual(response.status_code, 200, response.content)
        contract.refresh_from_db()
        self.assertEqual(contract.salary, Decimal("9000000.50"))
        self.assertEqual(contract.employee_id, employee.pk)
        self.assertEqual(contract.type, Contract.Type.FIXED)
        self.assertEqual(contract.display_status, "active")
        self.assertEqual(Contract.objects.count(), 1)

    def test_invalid_contracts_never_write_to_db(self):
        employee = self.create_employee()
        baseline = self.contract_input(employee)
        invalid = [{"salary": "0"}, {"salary": "-1"}, {"salary": "1.001"}, {"salary": "not-a-number"}, {"end_date": baseline["start_date"]}, {"end_date": ""}, {"signed_date": baseline["end_date"]}, {"employee_id": "MISSING"}, {"type": "Not a contract"}, {"start_date": ""}]
        for change in invalid:
            with self.subTest(change=change):
                data = baseline | change
                response = self.post(reverse("employees:contract_save"), data)
                self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(Contract.objects.count(), 0)

    def test_indefinite_contract_and_overlap(self):
        employee = self.create_employee()
        data = self.contract_input(employee) | {"type": "Không xác định thời hạn", "end_date": ""}
        response = self.post(reverse("employees:contract_save"), data)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIsNone(Contract.objects.get().end_date)
        response = self.post(reverse("employees:contract_save"), self.contract_input(employee))
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(Contract.objects.count(), 1)

    def test_renewal_overlap_is_a_validation_error(self):
        employee = self.create_employee()
        first = self.create_contract(employee)
        second_start = first.end_date + timedelta(days=1)
        self.create_contract(employee, start=second_start, end=second_start + timedelta(days=365))
        response = self.post(reverse("employees:contract_update", args=[first.pk]), {"renewal_date": "", "end_date": (second_start + timedelta(days=1)).isoformat(), "salary": "9000000"})
        self.assertEqual(response.status_code, 400, response.content)
        first.refresh_from_db()
        self.assertEqual(first.salary, Decimal("8500000.25"))

    def test_deactivation_keeps_history_and_blocks_linked_login(self):
        employee = self.create_employee(user=self.staff)
        contract = self.create_contract(employee)
        response = self.post(reverse("employees:employee_deactivate", args=[employee.pk]), {"end_date": timezone.localdate().isoformat(), "reason": "Nghỉ việc theo nguyện vọng"})
        self.assertEqual(response.status_code, 200, response.content)
        employee.refresh_from_db()
        self.staff.refresh_from_db()
        self.assertFalse(employee.is_active)
        self.assertFalse(self.staff.is_active)
        self.assertTrue(Contract.objects.filter(pk=contract.pk).exists())
        self.assertFalse(Client().login(username="staff", password="Staff-Test-938!"))
        self.assertEqual(self.post(reverse("employees:contract_save"), self.contract_input(employee)).status_code, 400)
        self.assertEqual(self.post(reverse("employees:employee_deactivate", args=[employee.pk]), {"end_date": timezone.localdate().isoformat(), "reason": "Again"}).status_code, 409)

    def test_invalid_departure_and_self_deactivation_are_rejected(self):
        employee = self.create_employee(user=self.manager)
        response = self.post(reverse("employees:employee_deactivate", args=[employee.pk]), {"end_date": timezone.localdate().isoformat(), "reason": "Self"})
        self.assertEqual(response.status_code, 400)
        other = self.create_employee(2)
        for change in [{"reason": ""}, {"end_date": "1999-01-01"}, {"end_date": (timezone.localdate() + timedelta(days=1)).isoformat()}]:
            response = self.post(reverse("employees:employee_deactivate", args=[other.pk]), {"end_date": timezone.localdate().isoformat(), "reason": "Reason"} | change)
            self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(Employee.objects.filter(is_active=True).count(), 2)

    def test_staff_cannot_read_others_or_forge_manager_role(self):
        own = self.create_employee(user=self.staff)
        other = self.create_employee(2)
        self.create_contract(own)
        self.create_contract(other)
        staff_client = Client()
        staff_client.force_login(self.staff)
        for route in [reverse("employees:employee_list"), reverse("employees:employee_detail", args=[other.pk]), reverse("employees:contract_list")]:
            self.assertEqual(staff_client.get(route + "?role=manager").status_code, 403)
        self.assertEqual(self.post(reverse("employees:employee_save") + "?role=manager", self.employee_input(3), staff_client).status_code, 403)
        data = staff_client.get(reverse("employees:my_contracts")).context["bootstrap"]
        self.assertEqual([item["id"] for item in data["employees"]], [own.pk])
        self.assertEqual([item["employee_id"] for item in data["contracts"]], [own.pk])
        self.assertNotIn(other.email, json.dumps(data))

    def test_authentication_csrf_and_post_required(self):
        url = reverse("employees:employee_save")
        self.assertEqual(Client().get(reverse("employees:employee_list")).status_code, 302)
        self.assertEqual(self.post(url, self.employee_input(), Client()).status_code, 401)
        self.assertEqual(self.client.get(url).status_code, 405)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.manager)
        page = client.get(reverse("employees:employee_list"))
        self.assertEqual(page.status_code, 200)
        self.assertEqual(self.post(url, self.employee_input(), client).status_code, 403)
        response = client.post(url, json.dumps(self.employee_input()), content_type="application/json", HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 200, response.content)

    def test_bad_requests_and_missing_records(self):
        url = reverse("employees:employee_save")
        for body in ["not JSON", "[]", '{"name": null}']:
            self.assertEqual(self.client.post(url, body, content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post(url, {"name": "wrong type"}).status_code, 400)
        self.assertEqual(self.post(reverse("employees:employee_update", args=["MISSING"]), self.employee_input()).status_code, 404)
        self.assertEqual(self.client.get(reverse("employees:employee_detail", args=["MISSING"])).status_code, 404)

    def test_database_constraints_and_delete_protection(self):
        employee = self.create_employee()
        contract = self.create_contract(employee)
        with self.assertRaises(ValidationError):
            employee.delete()
        with self.assertRaises(ValidationError):
            Employee.objects.all().delete()
        with self.assertRaises(ProtectedError):
            self.department.delete()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Contract.objects.filter(pk=contract.pk).update(salary=0)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Contract.objects.filter(pk=contract.pk).update(end_date=None)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Employee.objects.filter(pk=employee.pk).update(is_active=False)

    def test_status_changes_with_server_date(self):
        employee = self.create_employee()
        contract = self.create_contract(employee)
        with patch("apps.employees.models.timezone.localdate", return_value=contract.start_date - timedelta(days=1)):
            self.assertEqual(contract.display_status, "upcoming")
        with patch("apps.employees.models.timezone.localdate", return_value=contract.end_date + timedelta(days=1)):
            self.assertEqual(contract.display_status, "expired")
        with patch("apps.employees.models.timezone.localdate", return_value=contract.end_date):
            self.assertEqual(contract.display_status, "active")
