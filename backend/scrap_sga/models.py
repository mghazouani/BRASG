from django.db import models

# Create your models here.

class ScrapDimagazBC(models.Model):
    odoo_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=100)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    bc_date = models.DateTimeField(null=True, blank=True)
    bl_date = models.DateTimeField(null=True, blank=True)
    fournisseur = models.ForeignKey('ScrapFournisseur', null=True, blank=True, on_delete=models.SET_NULL, related_name='bcs')
    fournisseur_centre = models.ForeignKey('ScrapFournisseurCentre', null=True, blank=True, on_delete=models.SET_NULL, related_name='bcs')
    depositaire = models.ForeignKey('ScrapUser', null=True, blank=True, on_delete=models.SET_NULL, related_name='bcs')
    montant_paye = models.FloatField(null=True, blank=True)
    done = models.BooleanField(default=False)
    sap = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    remise = models.FloatField(null=True, blank=True)
    tva = models.FloatField(null=True, blank=True)
    ht = models.FloatField(null=True, blank=True)
    ttc = models.FloatField(null=True, blank=True)
    bc_type = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    terminated = models.BooleanField(default=False)
    verify_state = models.CharField(max_length=50, null=True, blank=True)
    qty_retenue = models.FloatField(null=True, blank=True)
    paye_par = models.CharField(max_length=50, null=True, blank=True)
    bl_number = models.CharField(max_length=50, null=True, blank=True)
    solde = models.FloatField(null=True, blank=True)
    non_conforme = models.BooleanField(default=False)
    version = models.CharField(max_length=50, blank=True, null=True)
    prefix = models.BooleanField(default=False)
    source = models.CharField(max_length=50, null=True, blank=True)
    product_type = models.CharField(max_length=50, null=True, blank=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    write_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"BC {self.name} (Odoo {self.odoo_id})"

class ScrapDimagazBCLine(models.Model):
    odoo_id = models.IntegerField(unique=True, db_index=True)
    bc = models.ForeignKey('ScrapDimagazBC', on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey('ScrapProduct', null=True, blank=True, on_delete=models.SET_NULL, related_name='bc_lines')
    product_name = models.CharField(max_length=100, null=True, blank=True)
    qty = models.FloatField(null=True, blank=True)
    qty_vide = models.FloatField(null=True, blank=True)
    qty_retenue = models.FloatField(null=True, blank=True)
    qty_defect = models.FloatField(null=True, blank=True)
    prix = models.FloatField(null=True, blank=True)
    subtotal = models.FloatField(null=True, blank=True)
    bc_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    write_date = models.DateTimeField(null=True, blank=True)
    # Ajoute ici tout autre champ Odoo à synchroniser

    def __str__(self):
        return f"BC Line {self.odoo_id} (Produit {self.product_name})"

class ScrapProduct(models.Model):
    odoo_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=100)
    product_id = models.IntegerField()
    product_id_name = models.CharField(max_length=100, blank=True, null=True)
    product_category = models.IntegerField(blank=True, null=True)
    product_category_name = models.CharField(max_length=100, blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_type = models.CharField(max_length=50, blank=True, null=True)
    display_name = models.CharField(max_length=150, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    write_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.display_name or self.name

class ScrapFournisseur(models.Model):
    odoo_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    ville = models.CharField(max_length=100, null=True, blank=True)
    centre_ids = models.JSONField(null=True, blank=True)  # liste d'IDs Odoo des centres
    create_date = models.DateTimeField(null=True, blank=True)
    write_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class ScrapFournisseurCentre(models.Model):
    odoo_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    fournisseur = models.ForeignKey('ScrapFournisseur', null=True, blank=True, on_delete=models.SET_NULL, related_name='centres')
    create_date = models.DateTimeField(null=True, blank=True)
    write_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class ScrapUser(models.Model):
    odoo_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    sap_id = models.CharField(max_length=64)
    create_date = models.DateTimeField(null=True, blank=True)
    write_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.display_name

class AuditLog(models.Model):
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)
    action = models.CharField(max_length=20)  # created, updated, deleted
    changed_by = models.CharField(max_length=100, null=True, blank=True)  # script, admin, etc.
    change_time = models.DateTimeField(auto_now_add=True)
    diff = models.JSONField(null=True, blank=True)  # Avant/Après ou valeurs modifiées
    source = models.CharField(max_length=50, default='sync_script')

    def __str__(self):
        return f"[{self.change_time}] {self.model_name}({self.object_id}) {self.action} by {self.changed_by or self.source}"

class ScrappingConsole(models.Model):
    SCRAP_CHOICES = [
        ('sync_user', 'sync_user'),
        ('sync_products', 'sync_products'),
        ('sync_FounisseursCentres', 'sync_FounisseursCentres'),
        ('sync_BcLinbc', 'sync_BcLinbc'),
    ]
    scrap_type = models.CharField(max_length=40, choices=SCRAP_CHOICES)
    last_run = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='idle')  # idle, running, success, failed
    params = models.JSONField(default=dict, blank=True)  # ex: {"batch_size": 10, "last": 100}
    result = models.TextField(blank=True)  # logs ou résumé du dernier run
    auto_schedule = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True, help_text="Expression cron si auto_schedule")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Scrap {self.scrap_type} ({self.status})"

class SyncState(models.Model):
    name = models.CharField(max_length=100, unique=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    is_syncing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (last_sync: {self.last_sync}, syncing: {self.is_syncing})"

class SyncLog(models.Model):
    sync_type = models.CharField(max_length=100)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('success', 'Succès'), ('error', 'Erreur'), ('partial', 'Partiel')])
    details = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    bc_synced = models.IntegerField(null=True, blank=True)
    line_synced = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"[{self.sync_type}] {self.start_time} - {self.status}"
