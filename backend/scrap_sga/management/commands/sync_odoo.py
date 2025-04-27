import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from django.conf import settings
from scrap_sga.models import ScrapDimagazBC, ScrapDimagazBCLine, ScrapFournisseur, ScrapFournisseurCentre, ScrapUser, ScrapProduct
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

def to_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ('1', 'true', 'yes', 'y', 'vrai', 'oui', 'on')
    return False

class Command(BaseCommand):
    help = 'Synchronise les BC et lignes BC depuis Odoo vers la base locale (anti-doublon, upsert)'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=100, help='Taille du batch pour la synchro Odoo')
        parser.add_argument('--last', type=int, default=None, help='Limiter aux X derniers BC (et leurs lignes)')
        parser.add_argument('--name', type=str, default=None, help='Filtrer sur le champ name de dimagaz.bc')

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        last = options['last']
        name = options['name']
        self.stdout.write(self.style.NOTICE(f'Connexion à Odoo... (batch_size={batch_size}, last={last}, name={name})'))
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            self.stdout.write(self.style.ERROR('Echec authentification Odoo'))
            return
        self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        # Recherche filtrée sur name si précisé
        bc_search_domain = []
        if name:
            bc_search_domain.append(('name', '=', name))
        bc_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'search', [bc_search_domain], {'order': 'id desc'})
        if last:
            bc_ids = bc_ids[:last]
        bc_ids = list(reversed(bc_ids))
        self.stdout.write(f"{len(bc_ids)} BC trouvés.")
        for offset in range(0, len(bc_ids), batch_size):
            batch_ids = bc_ids[offset:offset+batch_size]
            bc_records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'read', [batch_ids]
            )
            self.stdout.write(f"Traitement du batch {offset//batch_size + 1} : {len(batch_ids)} BC...")
            for bc in bc_records:
                # Résolution des FK Odoo
                fournisseur_obj = None
                fournisseur_centre_obj = None
                depositaire_obj = None
                fournisseur_id = bc.get('fournisseur', [None])[0]
                if fournisseur_id:
                    fournisseur_obj = ScrapFournisseur.objects.filter(odoo_id=fournisseur_id).first()
                fournisseur_centre_id = bc.get('fournisseur_centre', [None])[0]
                if fournisseur_centre_id:
                    fournisseur_centre_obj = ScrapFournisseurCentre.objects.filter(odoo_id=fournisseur_centre_id).first()
                depositaire_id = bc.get('depositaire', [None])[0]
                if depositaire_id:
                    depositaire_obj = ScrapUser.objects.filter(odoo_id=depositaire_id).first()
                with transaction.atomic():
                    bc_obj, created = ScrapDimagazBC.objects.update_or_create(
                        odoo_id=bc['id'],
                        defaults={
                            'name': bc.get('name', ''),
                            'fullname': bc.get('fullname', ''),
                            'bc_date': parse_odoo_datetime(bc.get('bc_date')),
                            'bl_date': parse_odoo_datetime(bc.get('bl_date')),
                            'fournisseur': fournisseur_obj,
                            'fournisseur_centre': fournisseur_centre_obj,
                            'depositaire': depositaire_obj,
                            'montant_paye': round(float(bc.get('montant_paye', 0.0)), 2) if bc.get('montant_paye') is not None else None,
                            'done': to_bool(bc.get('done')),
                            'sap': to_bool(bc.get('sap')),
                            'confirmed': to_bool(bc.get('confirmed')),
                            'remise': bc.get('remise'),
                            'tva': bc.get('tva'),
                            'ht': round(float(bc.get('ht', 0.0)), 2) if bc.get('ht') is not None else None,
                            'ttc': round(float(bc.get('ttc', 0.0)), 2) if bc.get('ttc') is not None else None,
                            'bc_type': bc.get('bc_type', ''),
                            'state': bc.get('state', ''),
                            'terminated': to_bool(bc.get('terminated')),
                            'verify_state': bc.get('verify_state', ''),
                            'qty_retenue': bc.get('qty_retenue'),
                            'paye_par': bc.get('paye_par', ''),
                            'bl_number': bc.get('bl_number', ''),
                            'solde': round(float(bc.get('solde', 0.0)), 2) if bc.get('solde') is not None else None,
                            'non_conforme': to_bool(bc.get('non_conforme')),
                            'version': to_bool(bc.get('version')),
                            'prefix': to_bool(bc.get('prefix')),
                            'source': bc.get('source', ''),
                            'product_type': bc.get('product_type', ''),
                            'display_name': bc.get('display_name', ''),
                            'create_date': parse_odoo_datetime(bc.get('create_date')),
                            'write_date': parse_odoo_datetime(bc.get('write_date')),
                        }
                    )
                    # --- Synchronisation des lignes pour ce BC ---
                    line_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'search', [[('bc_id', '=', bc['id'])]])
                    if line_ids:
                        line_records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'read', [line_ids])
                        for line in line_records:
                            # Résolution de la FK produit
                            product_obj = None
                            product_id = line.get('product', [None])[0]
                            if product_id:
                                product_obj = ScrapProduct.objects.filter(odoo_id=product_id).first()
                            ScrapDimagazBCLine.objects.update_or_create(
                                odoo_id=line['id'],
                                defaults={
                                    'bc': bc_obj,
                                    'product': product_obj,
                                    'product_name': line.get('product', [None, None])[1],
                                    'qty': line.get('qty'),
                                    'qty_vide': line.get('qty_vide'),
                                    'qty_retenue': line.get('qty_retenue'),
                                    'qty_defect': line.get('qty_defect'),
                                    'prix': line.get('prix'),
                                    'subtotal': round(float(line.get('subtotal', 0.0)), 2) if line.get('subtotal') is not None else None,
                                    'bc_date': parse_odoo_datetime(line.get('bc_date')),
                                    'create_date': parse_odoo_datetime(line.get('create_date')),
                                    'write_date': parse_odoo_datetime(line.get('write_date')),
                                }
                            )
        self.stdout.write(self.style.SUCCESS('Synchronisation terminée.'))
