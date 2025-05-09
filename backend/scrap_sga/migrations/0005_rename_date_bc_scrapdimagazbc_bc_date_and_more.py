# Generated by Django 4.2.20 on 2025-04-27 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("scrap_sga", "0004_scrapuser"),
    ]

    operations = [
        migrations.RenameField(
            model_name="scrapdimagazbc",
            old_name="date_bc",
            new_name="bc_date",
        ),
        migrations.RenameField(
            model_name="scrapdimagazbc",
            old_name="etat",
            new_name="bc_type",
        ),
        migrations.RemoveField(
            model_name="scrapdimagazbc",
            name="depositaire_id",
        ),
        migrations.RemoveField(
            model_name="scrapdimagazbc",
            name="depositaire_name",
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="bl_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="bl_number",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="confirmed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="depositaire",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bcs",
                to="scrap_sga.scrapuser",
            ),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="display_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="done",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="fournisseur",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bcs",
                to="scrap_sga.scrapfournisseur",
            ),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="fournisseur_centre",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bcs",
                to="scrap_sga.scrapfournisseurcentre",
            ),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="fullname",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="ht",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="montant_paye",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="non_conforme",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="paye_par",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="prefix",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="product_type",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="qty_retenue",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="remise",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="sap",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="solde",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="source",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="state",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="terminated",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="ttc",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="tva",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="verify_state",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="scrapdimagazbc",
            name="version",
            field=models.BooleanField(default=False),
        ),
    ]
