# Generated by Django 5.1.2 on 2024-11-08 12:19

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_demand_leasedenddate'),
    ]

    operations = [
        migrations.AddField(
            model_name='demand',
            name='created_at',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='demand',
            name='updated_at',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
