# Generated by Django 4.2.13 on 2024-06-19 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal', '0006_recursivelist_collapsed'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfiniteList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opml', models.TextField()),
            ],
        ),
    ]
