# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-07 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0032_auto_20160507_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='show_time',
            field=models.DateField(null=True),
        ),
    ]
