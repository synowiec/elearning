# Generated by Django 3.0.5 on 2020-05-10 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0011_auto_20200510_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerhistory',
            name='is_correct',
            field=models.BooleanField(),
        ),
    ]
