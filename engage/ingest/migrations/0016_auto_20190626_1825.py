# Generated by Django 2.0.12 on 2019-06-26 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0015_auto_20190626_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agenda',
            name='cutoff_time',
            field=models.PositiveIntegerField(default=1561573539.928701),
        ),
        migrations.AlterField(
            model_name='agenda',
            name='pdf_time',
            field=models.PositiveIntegerField(default=1561573539.928747),
        ),
    ]
