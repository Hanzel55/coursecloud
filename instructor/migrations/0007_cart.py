# Generated by Django 5.1.5 on 2025-02-05 11:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instructor", "0006_lesson"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "course_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="instructor.course",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="basket",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
