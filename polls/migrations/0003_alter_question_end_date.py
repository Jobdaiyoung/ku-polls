# Generated by Django 4.2.4 on 2023-09-11 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0002_question_end_date_alter_question_pub_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True, verbose_name="end date"),
        ),
    ]
