# Generated by Django 5.1.2 on 2024-10-22 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StockData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10)),
                ('date', models.DateField()),
                ('open_price', models.FloatField()),
                ('close_price', models.FloatField()),
                ('volume', models.IntegerField()),
            ],
        ),
    ]
