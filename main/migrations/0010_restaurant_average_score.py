# Generated by Django 2.2.4 on 2020-10-31 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20201031_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='average_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
