# Generated by Django 2.0 on 2018-12-01 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processes', '0005_auto_20181201_0355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipo',
            name='nombre',
            field=models.CharField(db_column='NOMBRE', max_length=45),
        ),
    ]
