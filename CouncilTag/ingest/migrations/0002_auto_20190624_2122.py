# Generated by Django 2.0.12 on 2019-06-24 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='committee',
            name='location_lat',
        ),
        migrations.RemoveField(
            model_name='committee',
            name='location_lng',
        ),
        migrations.AddField(
            model_name='agenda',
            name='cutoff_time',
            field=models.PositiveIntegerField(default=1561411343.162474),
        ),
        migrations.AddField(
            model_name='agenda',
            name='pdf_location',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='agenda',
            name='pdf_time',
            field=models.PositiveIntegerField(default=1561411343.162521),
        ),
        migrations.AddField(
            model_name='committee',
            name='agendas_table_location',
            field=models.CharField(default='https://www.smgov.net/departments/clerk/agendas.aspx', max_length=255),
        ),
        migrations.AddField(
            model_name='committee',
            name='base_agenda_location',
            field=models.CharField(default='http://santamonicacityca.iqm2.com/Citizens/Detail_Meeting.aspx?ID=', max_length=255),
        ),
    ]