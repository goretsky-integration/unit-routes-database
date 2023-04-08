# Generated by Django 4.1.7 on 2023-04-08 07:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_roles', '0002_alter_userrole_options_alter_userrole_access_code_and_more'),
        ('telegram', '0002_telegramchat_created_at_alter_telegramchat_role'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='telegramchat',
            options={'verbose_name': 'telegram|model|telegram_chat', 'verbose_name_plural': 'telegram|model|telegram_chats'},
        ),
        migrations.AlterField(
            model_name='telegramchat',
            name='chat_id',
            field=models.BigIntegerField(db_index=True, unique=True, verbose_name='telegram|model|telegram_chat|chat_id'),
        ),
        migrations.AlterField(
            model_name='telegramchat',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='telegram|model|telegram_chat|created_at'),
        ),
        migrations.AlterField(
            model_name='telegramchat',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_roles.userrole', verbose_name='Telegram|model|telegram_chat|role'),
        ),
        migrations.AlterField(
            model_name='telegramchat',
            name='title',
            field=models.CharField(max_length=64, verbose_name='telegram|model|telegram_chat|title'),
        ),
        migrations.AlterField(
            model_name='telegramchat',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Telegram|model|telegram_chat|chat_type|private'), (2, 'Telegram|model|telegram_chat|chat_type|group')], verbose_name='Telegram|model|telegram_chat|type'),
        ),
        migrations.AlterField(
            model_name='telegramchat',
            name='username',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='telegram|model|telegram_chat|username'),
        ),
    ]