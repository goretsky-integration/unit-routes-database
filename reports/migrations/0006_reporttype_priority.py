# Generated by Django 4.1.7 on 2024-04-28 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_rename_verbose_name_reporttype_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporttype',
            name='priority',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='reports|model|report_type|priority'),
        ),
    ]
