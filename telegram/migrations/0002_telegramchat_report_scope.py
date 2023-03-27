# Generated by Django 4.1.7 on 2023-03-27 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scopes', '0002_reportscope_name_alter_reportscope_access_token'),
        ('telegram', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramchat',
            name='report_scope',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='scopes.reportscope'),
        ),
    ]
