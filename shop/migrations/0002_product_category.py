# Generated by Django 5.1.5 on 2025-02-18 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.CharField(
                choices=[
                    ("joker", "Joker"),
                    ("skins", "Skins"),
                    ("opponents", "Opponents"),
                ],
                default="skins",
                max_length=20,
            ),
        ),
    ]
