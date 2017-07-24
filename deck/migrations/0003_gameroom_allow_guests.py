# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-24 13:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deck', '0002_auto_20170724_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameroom',
            name='allow_guests',
            field=models.BooleanField(default=True, help_text='Allow anyone to play with the secret key without signing in'),
        ),
    ]