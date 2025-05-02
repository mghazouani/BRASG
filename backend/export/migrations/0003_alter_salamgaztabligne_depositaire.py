from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("export", "0002_salamgaztabligne"),
        ("scrap_sga", "0014_synclog_syncstate_is_syncing"),
    ]

    operations = [
        migrations.AlterField(
            model_name="salamgaztabligne",
            name="depositaire",
            field=models.ForeignKey(
                to="scrap_sga.scrapuser",
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                verbose_name="Dépositaire"
            ),
        ),
    ]
