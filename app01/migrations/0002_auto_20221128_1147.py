# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2022-11-28 03:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='blog',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.Blog'),
        ),
    ]
