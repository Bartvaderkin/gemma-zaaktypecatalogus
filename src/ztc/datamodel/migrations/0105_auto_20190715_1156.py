# Generated by Django 2.2.3 on 2019-07-15 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0104_auto_20190712_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklistitem',
            name='verplicht',
            field=models.BooleanField(default=False, help_text='Het al dan niet verplicht zijn van controle van het aandachtspunt voorafgaand aan het bereiken van de status van het gerelateerde STATUSTYPE.', verbose_name='verplicht'),
        ),
        migrations.AlterField(
            model_name='statustype',
            name='informeren',
            field=models.BooleanField(default=False, help_text='Aanduiding die aangeeft of na het zetten van een STATUS van dit STATUSTYPE de Initiator moet worden geïnformeerd over de statusovergang.', verbose_name='informeren'),
        ),
        migrations.AlterField(
            model_name='zaakobjecttype',
            name='ander_objecttype',
            field=models.BooleanField(default=False, help_text='Aanduiding waarmee wordt aangegeven of het ZAAKOBJECTTYPE een ander, niet in RSGB en RGBZ voorkomend, objecttype betreft', verbose_name='ander objecttype'),
        ),
    ]
