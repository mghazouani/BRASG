# Generated by Django 4.2.20 on 2025-05-04 11:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("export", "0007_alter_salamgaztabligne_prix_12kg_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="salamgaztab",
            name="inclure_tous_depositaires",
            field=models.BooleanField(
                default=False, verbose_name="Inclure tous les dépositaires"
            ),
        ),
    ]
