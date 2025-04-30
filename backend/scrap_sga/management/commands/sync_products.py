import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from scrap_sga.models import ScrapProduct
from scrap_sga.utils_audit import log_audit, compute_diff, log_delete
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from django.forms.models import model_to_dict

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

def parse_odoo_datetime(dt_str):
    if not dt_str:
        return None
    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    return timezone.make_aware(dt, dt_timezone.utc)

class Command(BaseCommand):
    help = 'Synchronise les produits Odoo (dimagaz.product) vers ScrapProduct.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Connexion à Odoo...'))
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            self.stdout.write(self.style.ERROR('Echec authentification Odoo'))
            return
        self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        product_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.product', 'search', [[]])
        self.stdout.write(f"{len(product_ids)} produits trouvés.")
        for offset in range(0, len(product_ids), 100):
            batch_ids = product_ids[offset:offset+100]
            records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.product', 'read', [batch_ids])
            for prod in records:
                # Extraction robuste de l'id produit (et autres champs relationnels si besoin)
                product_id_val = prod.get('product_id', None)
                if isinstance(product_id_val, (list, tuple)) and product_id_val:
                    product_id = product_id_val[0]
                    product_id_name = product_id_val[1] if len(product_id_val) > 1 else ''
                elif isinstance(product_id_val, int):
                    product_id = product_id_val
                    product_id_name = ''
                else:
                    product_id = None
                    product_id_name = ''

                product_category_val = prod.get('product_category', None)
                if isinstance(product_category_val, (list, tuple)) and product_category_val:
                    product_category = product_category_val[0]
                    product_category_name = product_category_val[1] if len(product_category_val) > 1 else ''
                elif isinstance(product_category_val, int):
                    product_category = product_category_val
                    product_category_name = ''
                else:
                    product_category = None
                    product_category_name = ''

                old_obj = ScrapProduct.objects.filter(odoo_id=prod['id']).first()
                obj, created = ScrapProduct.objects.update_or_create(
                    odoo_id=prod['id'],
                    defaults={
                        'name': prod.get('name', ''),
                        'product_id': product_id,
                        'product_id_name': product_id_name,
                        'product_category': product_category,
                        'product_category_name': product_category_name,
                        'prix': prod.get('prix', 0.0),
                        'product_type': prod.get('product_type', ''),
                        'display_name': prod.get('display_name', ''),
                        'create_date': parse_odoo_datetime(prod.get('create_date')),
                        'write_date': parse_odoo_datetime(prod.get('write_date')),
                    }
                )
                diff = compute_diff(old_obj, obj) if not created else None
                log_audit(obj, 'created' if created else 'updated', changed_by='sync_products', diff=diff, source='sync_script')
        # Suppression des produits locaux absents d'Odoo
        odoo_ids = set(product_ids)
        local_ids = set(ScrapProduct.objects.values_list('odoo_id', flat=True))
        to_delete = local_ids - odoo_ids
        for del_id in to_delete:
            obj = ScrapProduct.objects.get(odoo_id=del_id)
            log_delete(obj, changed_by='sync_products', source='sync_script')
            obj.delete()
        self.stdout.write(self.style.SUCCESS('Synchronisation produits terminée.'))
