# Generated by Django 4.2.3 on 2023-10-15 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('space', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='description',
            field=models.TextField(default=None, null=True),
        ),
    ]
