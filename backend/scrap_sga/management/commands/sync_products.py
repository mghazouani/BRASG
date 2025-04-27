import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from scrap_sga.models import ScrapProduct
from django.utils import timezone
from datetime import datetime

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

def parse_odoo_datetime(dt_str):
    if not dt_str:
        return None
    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    return timezone.make_aware(dt, timezone.utc)

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
                ScrapProduct.objects.update_or_create(
                    odoo_id=prod['id'],
                    defaults={
                        'name': prod.get('name', ''),
                        'product_id': prod.get('product_id', [None])[0] if isinstance(prod.get('product_id'), list) else prod.get('product_id'),
                        'product_id_name': prod.get('product_id', [None, None])[1] if isinstance(prod.get('product_id'), list) and len(prod.get('product_id')) > 1 else '',
                        'product_category': prod.get('product_category', [None])[0] if isinstance(prod.get('product_category'), list) else prod.get('product_category'),
                        'product_category_name': prod.get('product_category', [None, None])[1] if isinstance(prod.get('product_category'), list) and len(prod.get('product_category')) > 1 else '',
                        'prix': prod.get('prix'),
                        'product_type': prod.get('product_type', ''),
                        'display_name': prod.get('display_name', ''),
                        'create_date': parse_odoo_datetime(prod.get('create_date')),
                        'write_date': parse_odoo_datetime(prod.get('write_date')),
                    }
                )
        self.stdout.write(self.style.SUCCESS('Synchronisation produits terminée.'))
