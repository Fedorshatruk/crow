# Generated by Django 3.1.5 on 2021-01-27 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20210127_1014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='settings',
        ),
        migrations.AddField(
            model_name='gamesetting',
            name='session',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='core.session', verbose_name='Номер сессии'),
        ),
    ]