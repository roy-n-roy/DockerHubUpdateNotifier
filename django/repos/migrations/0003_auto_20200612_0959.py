# Generated by Django 3.0.7 on 2020-06-12 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repos', '0002_repositorytaghistory_watchinghistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repositorytag',
            name='last_updated',
            field=models.DateTimeField(),
        ),
    ]
