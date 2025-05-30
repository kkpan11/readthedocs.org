# Generated by Django 4.2.16 on 2024-11-13 12:01

from django.db import migrations
from django.db import models
from django_safemigrate import Safe


class Migration(migrations.Migration):
    safe = Safe.after_deploy()

    dependencies = [
        ("projects", "0134_addons_customscript"),
    ]

    operations = [
        migrations.AlterField(
            model_name="addonsconfig",
            name="options_load_when_embedded",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="historicaladdonsconfig",
            name="options_load_when_embedded",
            field=models.BooleanField(default=False),
        ),
    ]
