# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-05 03:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0027_auto_20160505_1155'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Torrent_Back',
            new_name='Torrent',
        ),
    ]
