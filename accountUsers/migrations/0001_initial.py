# Generated by Django 3.1 on 2020-10-17 10:45

import accountUsers.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='accountUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last_login')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('pro_pic', models.ImageField(blank=True, null=True, upload_to=accountUsers.models.upload_propic_image_path)),
                ('user_address', models.CharField(blank=True, max_length=255, null=True)),
                ('user_dob', models.DateField(max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
