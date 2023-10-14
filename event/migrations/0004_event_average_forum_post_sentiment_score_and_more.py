# Generated by Django 4.2.3 on 2023-10-14 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0003_alter_event_average_event_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='average_forum_post_sentiment_score',
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='number_of_post_sentiment_computed',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='average_event_rating',
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='average_sentiment_score',
            field=models.FloatField(default=None, null=True),
        ),
    ]
