# Generated by Django 5.1.3 on 2024-11-20 05:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProductManagement_APP', '0002_alter_productversion_batch_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('action_type', models.CharField(choices=[('IN', 'Stock In'), ('OUT', 'Stock Out')], max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_logs', to='ProductManagement_APP.productversion')),
            ],
        ),
    ]