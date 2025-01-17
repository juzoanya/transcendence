# Generated by Django 5.0.6 on 2024-05-12 21:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_gamerequest_game_id_gamerequest_game_mode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamerequest',
            name='tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_gr', to='game.tournament'),
        ),
        migrations.AddField(
            model_name='gameresults',
            name='tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_name', to='game.tournament'),
        ),
        migrations.AddField(
            model_name='gameschedule',
            name='tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_gs', to='game.tournament'),
        ),
        migrations.AlterField(
            model_name='tournamentlobby',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_tl', to='game.tournament'),
        ),
    ]
