# Generated by Django 4.1.1 on 2023-09-08 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='status',
            field=models.CharField(default='A', max_length=1),
        ),
    ]
