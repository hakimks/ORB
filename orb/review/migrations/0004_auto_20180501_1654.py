# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-01 16:54
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0003_update_pending_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentreview',
            name='status',
            field=django_fsm.FSMField(default='pending', max_length=50),
        ),
    ]
