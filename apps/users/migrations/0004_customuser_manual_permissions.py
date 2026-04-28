from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_can_view_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='can_delete_manual',
            field=models.BooleanField(default=False, verbose_name='صلاحية حذف يدوية'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='can_edit_manual',
            field=models.BooleanField(default=False, verbose_name='صلاحية تعديل يدوية'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='can_manage_users_manual',
            field=models.BooleanField(default=False, verbose_name='صلاحية إدارة المستخدمين يدويا'),
        ),
    ]
