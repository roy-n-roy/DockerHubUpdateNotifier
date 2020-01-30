# Generated by Django 3.0.2 on 2020-01-30 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='webhook_url',
            field=models.URLField(blank=True, help_text='If you would like to be notified by the chat tool, please obtain and enter your Webhook URL. Supported for Incoming Webhook URL of Slack and IFTTT.', max_length=500, null=True, verbose_name='Webhook URL'),
        ),
    ]