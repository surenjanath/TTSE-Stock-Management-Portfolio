# Generated by Django 4.2.6 on 2023-12-10 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_stock_information_ttse_issuedsharecap_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_information',
            name='No_days_since_start',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]