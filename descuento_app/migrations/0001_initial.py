# Generated by Django 5.1.6 on 2025-03-05 12:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('expiration_date', models.DateField()),
                ('state', models.BooleanField(default=True)),
                ('max_uses', models.IntegerField(default=1)),
                ('used_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RutDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rut', models.CharField(max_length=12)),
                ('used_count', models.IntegerField(default=0)),
                ('discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='descuento_app.discount')),
            ],
            options={
                'unique_together': {('rut', 'discount')},
            },
        ),
        migrations.CreateModel(
            name='DiscountUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boleta_number', models.CharField(max_length=50)),
                ('used_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('rut_discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='descuento_app.rutdiscount')),
            ],
        ),
    ]
