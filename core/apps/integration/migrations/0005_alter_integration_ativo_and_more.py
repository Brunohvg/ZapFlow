# Generated by Django 5.1.4 on 2025-02-11 22:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integration', '0004_alter_integration_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='integration',
            name='ativo',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='integration',
            name='configuracoes_extras',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterUniqueTogether(
            name='integration',
            unique_together={('user', 'tipo', 'nome')},
        ),
    ]
