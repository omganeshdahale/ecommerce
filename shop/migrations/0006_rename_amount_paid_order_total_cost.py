# Generated by Django 3.2.6 on 2021-08-24 07:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_alter_orderitem_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='amount_paid',
            new_name='total_cost',
        ),
    ]
