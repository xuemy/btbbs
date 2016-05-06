# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-31 03:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0009_auto_20160324_2222'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('son', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bbs.Category')),
            ],
        ),
    ]
