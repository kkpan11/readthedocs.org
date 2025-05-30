# Generated by Django 2.2.14 on 2020-07-27 15:47
from django.db import migrations
from django.db import models
from django_safemigrate import Safe


class Migration(migrations.Migration):
    safe = Safe.after_deploy()
    dependencies = [
        ("organizations", "0002_update_meta_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="auto_join_email_users",
            field=models.BooleanField(
                default=False,
                help_text="Auto join users with an organization's email address to this team.",
            ),
        ),
    ]
