from django.db import models

# Create your models here.

class SalamGazTab(models.Model):
    # Exemple de champs, à adapter selon besoin métier
    reference = models.CharField(max_length=100, verbose_name="Référence")
    date_export = models.DateTimeField(auto_now_add=True, verbose_name="Date d'export")
    description = models.TextField(blank=True, verbose_name="Description")
    date_debut = models.DateTimeField("Date début période", null=True, blank=True, help_text="Date et heure de début pour la génération automatique des lignes.")
    date_fin = models.DateTimeField("Date fin période", null=True, blank=True, help_text="Date et heure de fin pour la génération automatique des lignes.")

    class Meta:
        verbose_name = "SalamGaz Tab"
        verbose_name_plural = "SalamGaz Tabs"

    def __str__(self):
        return f"{self.reference} ({self.date_export:%Y-%m-%d})"

class SalamGazTabLigne(models.Model):
    export = models.ForeignKey(SalamGazTab, on_delete=models.CASCADE, related_name="lignes")
    client = models.CharField(max_length=100, verbose_name="Client")
    depositaire = models.CharField(max_length=100, verbose_name="Dépositaire")
    marque_bouteille = models.CharField(max_length=100, verbose_name="Marque Bouteille")
    qte_bd_3kg = models.PositiveIntegerField(default=0, verbose_name="Qté Bd 3KG")
    qte_bd_6kg = models.PositiveIntegerField(default=0, verbose_name="Qté Bd 6KG")
    qte_bd_12kg = models.PositiveIntegerField(default=0, verbose_name="Qté Bd 12KG")
    tonnage = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Tonnage (kg)")
    societe = models.CharField(max_length=100, verbose_name="Société")
    centre_emplisseur = models.CharField(max_length=100, verbose_name="Centre Emplisseur")
    mt_bl = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="MT BL")
    mt_vers_virt = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="MT VERS/VIRT")
    ecart = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Ecart")
    observation = models.TextField(blank=True, verbose_name="Observation")
    source_bcs = models.ManyToManyField(
        'scrap_sga.ScrapDimagazBC',
        blank=True,
        verbose_name="BC(s) source",
        help_text="Optionnel. Pour les lignes générées automatiquement : liste des BC à l'origine de cette ligne. Pour les ajouts manuels, peut être laissé vide."
    )

    def save(self, *args, **kwargs):
        # Calcul automatique de l'écart à chaque sauvegarde
        self.ecart = (self.mt_vers_virt or 0) - (self.mt_bl or 0)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Ligne SalamGaz Tab"
        verbose_name_plural = "Lignes SalamGaz Tab"

    def __str__(self):
        return f"{self.client} - {self.depositaire} - {self.marque_bouteille}"
