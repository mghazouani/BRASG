from django.db import models

# Create your models here.

class ScrapDimagazBC(models.Model):
    odoo_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=100)
    depositaire_id = models.IntegerField(null=True, blank=True)
    depositaire_name = models.CharField(max_length=100, null=True, blank=True)
    date_bc = models.DateTimeField(null=True, blank=True)
    etat = models.CharField(max_length=50, null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    write_date = models.DateTimeField(null=True, blank=True)
    # Ajoute ici tout autre champ Odoo à synchroniser

    def __str__(self):
        return f"BC {self.name} (Odoo {self.odoo_id})"

class ScrapDimagazBCLine(models.Model):
    odoo_id = models.IntegerField(unique=True, db_index=True)
    bc = models.ForeignKey('ScrapDimagazBC', on_delete=models.CASCADE, related_name='lines')
    product_id = models.IntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    qty = models.FloatField(null=True, blank=True)
    qty_vide = models.FloatField(null=True, blank=True)
    qty_retenue = models.FloatField(null=True, blank=True)
    qty_defect = models.FloatField(null=True, blank=True)
    prix = models.FloatField(null=True, blank=True)
    subtotal = models.FloatField(null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    write_date = models.DateTimeField(null=True, blank=True)
    # Ajoute ici tout autre champ Odoo à synchroniser

    def __str__(self):
        return f"BC Line {self.odoo_id} (Produit {self.product_name})"
