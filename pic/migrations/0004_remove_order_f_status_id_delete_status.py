# Generated by Django 5.0.7 on 2024-07-30 21:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pic', '0003_alter_accountmanager_user_alter_customer_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='f_status_id',
        ),
        migrations.DeleteModel(
            name='Status',
        ),
    ]
