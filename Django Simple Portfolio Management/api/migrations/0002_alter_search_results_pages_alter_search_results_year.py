# Generated by Django 4.2.6 on 2023-10-08 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search_results',
            name='pages',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='search_results',
            name='year',
            field=models.CharField(max_length=255),
        ),
    ]