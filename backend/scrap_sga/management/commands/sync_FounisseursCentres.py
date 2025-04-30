import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from django.db import transaction
from scrap_sga.models import ScrapFournisseur, ScrapFournisseurCentre
from scrap_sga.utils_audit import log_audit, compute_diff, log_delete
from datetime import datetime
from django.utils import timezone
from django.forms.models import model_to_dict

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

def parse_odoo_datetime(dt_str):
    if not dt_str:
        return None
    dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    return timezone.make_aware(dt, datetime.timezone.utc)

class Command(BaseCommand):
    help = 'Synchronise les fournisseurs et centres depuis Odoo (à la demande)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Connexion à Odoo...'))
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            self.stdout.write(self.style.ERROR('Echec authentification Odoo'))
            return
        self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        # --- Fournisseurs ---
        fournisseur_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.fournisseur', 'search', [[]])
        fournisseurs = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.fournisseur', 'read', [fournisseur_ids])
        self.stdout.write(f"{len(fournisseurs)} fournisseurs trouvés.")
        if fournisseurs:
            for f in fournisseurs:
                old_obj = ScrapFournisseur.objects.filter(odoo_id=f['id']).first()
                with transaction.atomic():
                    obj, created = ScrapFournisseur.objects.update_or_create(
                        odoo_id=f['id'],
                        defaults={
                            'name': f.get('name', ''),
                            'tel': f.get('tel', ''),
                            'adresse': f.get('adresse', ''),
                            'ville': f.get('ville', ''),
                            'email': f.get('email', ''),
                            'display_name': f.get('display_name', ''),
                        }
                    )
                    diff = compute_diff(old_obj, obj) if not created else None
                    log_audit(obj, 'created' if created else 'updated', changed_by='sync_FounisseursCentres', diff=diff, source='sync_script')

        # Suppression des fournisseurs locaux absents d'Odoo
        odoo_ids = set(fournisseur_ids)
        local_ids = set(ScrapFournisseur.objects.values_list('odoo_id', flat=True))
        to_delete = local_ids - odoo_ids
        for del_id in to_delete:
            obj = ScrapFournisseur.objects.get(odoo_id=del_id)
            log_delete(obj, changed_by='sync_FounisseursCentres', source='sync_script')
            obj.delete()

        # --- Centres ---
        centre_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.fournisseur.centre', 'search', [[]])
        centres = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.fournisseur.centre', 'read', [centre_ids])
        self.stdout.write(f"{len(centres)} centres trouvés.")
        if centres:
            # self.stdout.write(f"Champs centre : {list(centres[0].keys())}")
            for c in centres:
                fournisseur_obj = None
                centre_id_field = c.get('centre_id')
                fournisseur_id = centre_id_field[0] if isinstance(centre_id_field, list) and len(centre_id_field) > 0 else None
                if fournisseur_id:
                    fournisseur_obj = ScrapFournisseur.objects.filter(odoo_id=fournisseur_id).first()
                with transaction.atomic():
                    ScrapFournisseurCentre.objects.update_or_create(
                        odoo_id=c['id'],
                        defaults={
                            'name': c.get('display_name', ''),
                            'fournisseur': fournisseur_obj,
                            'create_date': parse_odoo_datetime(c.get('create_date')),
                            'write_date': parse_odoo_datetime(c.get('write_date')),
                        }
                    )
        self.stdout.write(self.style.SUCCESS('Synchronisation fournisseurs et centres terminée.'))
