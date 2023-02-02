# Generated by Django 4.1.5 on 2023-01-30 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='products',
            field=models.ManyToManyField(blank=True, null=True, related_name='users', to='api.product'),
        ),
    ]
