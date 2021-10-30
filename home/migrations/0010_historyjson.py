# Generated by Django 3.2.8 on 2021-10-29 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_alter_products_product_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryJson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product_json', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'History_JSON',
            },
        ),
    ]