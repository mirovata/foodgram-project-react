# Generated by Django 3.2.3 on 2024-02-20 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20240220_2035'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usersubscribe',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Пользовательскую подписку', 'verbose_name_plural': 'Пользовательские подписки'},
        ),
    ]
