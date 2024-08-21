# Generated by Django 5.1 on 2024-08-21 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_offer_status_offer_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='appointment',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Closed', 'Closed'), ('Deleted', 'Deleted')], default='Open', max_length=20),
        ),
    ]
