# Generated by Django 5.1.6 on 2025-03-05 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('descuento_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discount',
            name='used_count',
        ),
    ]
