# Generated by Django 5.1.3 on 2024-11-29 05:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Debt_Management', '0001_initial'),
        ('POS_APP', '0002_remove_transactionitem_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='Debt_Management.customer'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('Paid', 'Paid'), ('Pay Later', 'Pay Later')], default='Paid', max_length=10),
        ),
    ]
