# Generated by Django 3.0.3 on 2020-03-06 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0002_auto_20200306_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='end',
            field=models.DateField(blank=True),
        ),
    ]
