# Generated by Django 5.0 on 2023-12-24 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_challengesubmission_lambda_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challengesubmission',
            name='error_path',
        ),
        migrations.RemoveField(
            model_name='challengesubmission',
            name='output_path',
        ),
        migrations.AddField(
            model_name='challengesubmission',
            name='error',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='challengesubmission',
            name='output',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='challengesubmission',
            name='status',
            field=models.CharField(choices=[('not_ready', 'Not Ready'), ('ready', 'Ready'), ('running', 'Running'), ('success', 'Success'), ('failure', 'Failure')], default='not_ready', max_length=100),
        ),
    ]
