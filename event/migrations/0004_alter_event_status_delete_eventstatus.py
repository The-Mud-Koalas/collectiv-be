# Generated by Django 4.2.3 on 2023-08-23 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0003_alter_event_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('Scheduled', 'Scheduled'), ('On Going', 'On Going'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Scheduled', max_length=10),
        ),
        migrations.DeleteModel(
            name='EventStatus',
        ),
    ]