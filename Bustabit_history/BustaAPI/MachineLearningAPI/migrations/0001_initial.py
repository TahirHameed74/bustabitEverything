# Generated by Django 2.2.4 on 2020-07-24 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='anomaly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=256)),
                ('timeseries_column_name', models.CharField(max_length=100)),
                ('value_column_name', models.CharField(max_length=100)),
            ],
        ),
    ]
