# Generated by Django 3.2.6 on 2021-08-24 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_rename_amount_paid_order_total_cost'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-placed',)},
        ),
        migrations.RemoveField(
            model_name='order',
            name='created',
        ),
    ]