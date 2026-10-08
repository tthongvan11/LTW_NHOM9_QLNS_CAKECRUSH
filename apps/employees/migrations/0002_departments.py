from django.db import migrations


def create_departments(apps, schema_editor):
    Department = apps.get_model("employees", "Department")
    for code, name in [("BEP", "Bếp bánh"), ("CUAHANG", "Cửa hàng"), ("MARKETING", "Marketing"), ("KETOAN", "Kế toán"), ("BANHANG", "Bán hàng"), ("VANHANH", "Vận hành cửa hàng")]:
        Department.objects.using(schema_editor.connection.alias).get_or_create(id=code, defaults={"name": name})


class Migration(migrations.Migration):
    dependencies = [("employees", "0001_initial")]
    operations = [migrations.RunPython(create_departments, migrations.RunPython.noop)]
