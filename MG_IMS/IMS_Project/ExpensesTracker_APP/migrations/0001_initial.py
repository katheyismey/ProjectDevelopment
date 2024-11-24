# Generated by Django 5.1.3 on 2024-11-24 04:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ProductManagement_APP', '0005_rename_version_stocklog_product_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('buying_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=15)),
                ('product_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_logs', to='ProductManagement_APP.productversion')),
            ],
        ),
    ]