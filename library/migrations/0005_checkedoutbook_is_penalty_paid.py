# Generated by Django 5.0 on 2024-01-08 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_rename_borrowedbook_checkedoutbook'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkedoutbook',
            name='is_penalty_paid',
            field=models.BooleanField(default=False),
        ),
    ]
