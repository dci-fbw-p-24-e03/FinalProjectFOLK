# Generated by Django 5.1.5 on 2025-02-25 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_customuser_nation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='image',
            field=models.ImageField(default='/user_profile_images/profile_placeholder.jpeg', upload_to='user_profile_images/'),
        ),
    ]
