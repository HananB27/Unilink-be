# Generated by Django 5.2.1 on 2025-05-29 15:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_users_options_remove_users_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='user_permissions',
        ),
    ]
