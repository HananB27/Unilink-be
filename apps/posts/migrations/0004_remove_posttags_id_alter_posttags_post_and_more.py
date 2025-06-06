# Generated by Django 5.2.1 on 2025-06-02 14:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_posttags_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posttags',
            name='id',
        ),
        migrations.AlterField(
            model_name='posttags',
            name='post',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='posts.posts'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='posttags',
            name='tag',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.CASCADE, to='posts.tags'),
            preserve_default=False,
        ),
    ]
