# Generated by Django 2.0.9 on 2019-01-14 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0047_auto_20190114_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zaaktype',
            name='opschorting_en_aanhouding_mogelijk',
            field=models.BooleanField(help_text='Aanduiding die aangeeft of ZAAKen van dit mogelijk ZAAKTYPE kunnen worden opgeschort en/of aangehouden.', verbose_name='opschorting/aanhouding mogelijk'),
        ),
        migrations.AlterField(
            model_name='zaaktype',
            name='publicatie_indicatie',
            field=models.BooleanField(help_text='Aanduiding of (het starten van) een ZAAK dit ZAAKTYPE gepubliceerd moet worden.', verbose_name='publicatie indicatie'),
        ),
        migrations.AlterField(
            model_name='zaaktype',
            name='verlenging_mogelijk',
            field=models.BooleanField(help_text='Aanduiding die aangeeft of de Doorlooptijd behandeling van ZAAKen van dit ZAAKTYPE kan worden verlengd.', verbose_name='verlenging mogelijk'),
        ),
    ]
