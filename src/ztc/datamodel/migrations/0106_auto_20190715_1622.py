# Generated by Django 2.2.3 on 2019-07-15 14:22

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0105_auto_20190715_1156'),
    ]

    operations = [
        migrations.RenameField(
            model_name='zaakinformatieobjecttype',
            old_name='informatie_object_type',
            new_name='informatieobjecttype',
        ),
        migrations.RenameField(
            model_name='eigenschap',
            old_name='status_type',
            new_name='statustype',
        ),
        migrations.RenameField(
            model_name='zaakobjecttype',
            old_name='status_type',
            new_name='statustype',
        ),
        migrations.RenameField(
            model_name='zaakinformatieobjecttype',
            old_name='status_type',
            new_name='statustype',
        ),
    ]
