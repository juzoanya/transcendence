# Generated by Django 5.0.6 on 2024-05-16 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_gamerequest_tournament_gameresults_tournament_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='mode',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
    ]