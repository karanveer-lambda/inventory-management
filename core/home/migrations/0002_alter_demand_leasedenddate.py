# Generated by Django 5.1.2 on 2024-11-08 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demand',
            name='leasedEndDate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
