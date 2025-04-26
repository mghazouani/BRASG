import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from django.conf import settings
from scrap_sga.models import ScrapDimagazBC, ScrapDimagazBCLine
from django.db import transaction
from datetime import datetime
from django.utils import timezone

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
    help = 'Synchronise les BC et lignes BC depuis Odoo vers la base locale (anti-doublon, upsert)'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=100, help='Taille du batch pour la synchro Odoo')
        parser.add_argument('--last', type=int, default=None, help='Limiter aux X derniers BC (et leurs lignes)')

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        last = options['last']
        self.stdout.write(self.style.NOTICE(f'Connexion à Odoo... (batch_size={batch_size}, last={last})'))
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            self.stdout.write(self.style.ERROR('Echec authentification Odoo'))
            return
        self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        # --- Recherche des BC (avec limite si --last) ---
        bc_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'search', [[]], {'order': 'id desc'})
        if last:
            bc_ids = bc_ids[:last]
        bc_ids = list(reversed(bc_ids))  # Pour traiter dans l'ordre croissant d'id
        self.stdout.write(f"{len(bc_ids)} BC trouvés.")
        for offset in range(0, len(bc_ids), batch_size):
            batch_ids = bc_ids[offset:offset+batch_size]
            bc_records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'read', [batch_ids]
            )
            self.stdout.write(f"Traitement du batch {offset//batch_size + 1} : {len(batch_ids)} BC...")
            for bc in bc_records:
                with transaction.atomic():
                    bc_obj, created = ScrapDimagazBC.objects.update_or_create(
                        odoo_id=bc['id'],
                        defaults={
                            'name': bc.get('name', ''),
                            'depositaire_id': bc.get('depositaire', [None])[0],
                            'depositaire_name': bc.get('depositaire', [None, None])[1],
                            'date_bc': parse_odoo_datetime(bc.get('bc_date')),
                            'state': bc.get('state', ''),
                            'create_date': parse_odoo_datetime(bc.get('create_date')),
                            'write_date': parse_odoo_datetime(bc.get('write_date')),
                        }
                    )
                    # --- Synchronisation des lignes pour ce BC ---
                    line_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'search', [[('bc_id', '=', bc['id'])]])
                    if line_ids:
                        line_records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'read', [line_ids])
                        for line in line_records:
                            ScrapDimagazBCLine.objects.update_or_create(
                                odoo_id=line['id'],
                                defaults={
                                    'bc': bc_obj,
                                    'product_id': line.get('product', [None])[0],
                                    'product_name': line.get('product', [None, None])[1],
                                    'qty': line.get('qty'),
                                    'qty_vide': line.get('qty_vide'),
                                    'qty_retenue': line.get('qty_retenue'),
                                    'qty_defect': line.get('qty_defect'),
                                    'prix': line.get('prix'),
                                    'subtotal': line.get('subtotal'),
                                    'create_date': parse_odoo_datetime(line.get('create_date')),
                                    'write_date': parse_odoo_datetime(line.get('write_date')),
                                }
                            )
        self.stdout.write(self.style.SUCCESS('Synchronisation terminée.'))
