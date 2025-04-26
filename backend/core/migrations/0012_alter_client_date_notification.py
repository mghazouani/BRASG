from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_alter_client_region"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="date_notification",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
