# Generated by Django 4.2.16 on 2024-10-29 14:05

from django.db import migrations, models
from django_safemigrate import Safe


class Migration(migrations.Migration):
    safe = Safe.before_deploy

    dependencies = [
        ("projects", "0127_default_to_semver"),
    ]

    operations = [
        migrations.AddField(
            model_name="addonsconfig",
            name="notifications_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="addonsconfig",
            name="notifications_show_on_external",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="addonsconfig",
            name="notifications_show_on_latest",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="addonsconfig",
            name="notifications_show_on_non_stable",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="historicaladdonsconfig",
            name="notifications_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="historicaladdonsconfig",
            name="notifications_show_on_external",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="historicaladdonsconfig",
            name="notifications_show_on_latest",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="historicaladdonsconfig",
            name="notifications_show_on_non_stable",
            field=models.BooleanField(default=True),
        ),
    ]