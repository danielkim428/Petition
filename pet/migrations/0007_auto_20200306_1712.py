# Generated by Django 3.0.3 on 2020-03-06 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0006_post_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(blank=True, choices=[('Policy', 'Policy'), ('Academic', 'Academic'), ('Food', 'Food'), ('Event', 'Event')], max_length=20, null=True),
        ),
    ]
