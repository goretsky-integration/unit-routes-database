# Generated by Django 4.1.7 on 2024-04-28 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_rename_name_reporttype_verbose_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reporttype',
            old_name='alias',
            new_name='name',
        ),
    ]
