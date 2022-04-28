# Generated by Django 3.2.5 on 2022-01-26 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FormTypeCounter",
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
                ("form_type", models.CharField(max_length=5)),
                ("load_or_sub", models.CharField(max_length=4)),
            ],
        ),
    ]