# Generated by Django 2.2.4 on 2020-10-30 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20201029_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_done',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]