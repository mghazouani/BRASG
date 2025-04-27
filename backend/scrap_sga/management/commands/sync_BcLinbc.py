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
from scrap_sga.utils_audit import log_audit, compute_diff, log_delete
from django.forms.models import model_to_dict

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
        parser.add_argument('--date', type=int, default=None, help="Limiter aux BC créés ou modifiés dans les X dernières heures")

    def handle(self, *args, **options):
        # Vérification pré-scrap : les tables de référence ne doivent pas être vides
        missing_tables = []
        if ScrapUser.objects.count() == 0:
            missing_tables.append('users')
        if ScrapFournisseur.objects.count() == 0:
            missing_tables.append('fournisseurs')
        if ScrapFournisseurCentre.objects.count() == 0:
            missing_tables.append('centres')
        if ScrapProduct.objects.count() == 0:
            missing_tables.append('produits')
        if missing_tables:
            self.stdout.write(self.style.ERROR(f"ATTENTION : Les tables suivantes sont vides : {', '.join(missing_tables)}.\nVeuillez lancer d'abord la synchronisation de ces référentiels (users, fournisseurs, centres, produits) avant de lancer sync_BcLinbc."))
            return

        batch_size = options['batch_size']
        last = options['last']
        name = options['name']
        date_hours = options.get('date')
        if date_hours:
            since = timezone.now() - timezone.timedelta(hours=date_hours)
        self.stdout.write(self.style.NOTICE(f'Connexion à Odoo... (batch_size={batch_size}, last={last}, name={name}, date={date_hours})'))
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
        if date_hours:
            bc_search_domain.append(('write_date', '>=', since.strftime('%Y-%m-%d %H:%M:%S')))
        bc_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'search', [bc_search_domain], {'order': 'id desc'})
        if last:
            bc_ids = bc_ids[:last]
        bc_ids = list(reversed(bc_ids))
        self.stdout.write(f"{len(bc_ids)} BC trouvés.")
        
        # Suppression des BC locaux absents d'Odoo
        odoo_bc_ids = set(bc_ids)
        local_bc_ids = set(ScrapDimagazBC.objects.values_list('odoo_id', flat=True))
        to_delete_bc = local_bc_ids - odoo_bc_ids
        for del_id in to_delete_bc:
            obj = ScrapDimagazBC.objects.get(odoo_id=del_id)
            log_delete(obj, changed_by='sync_BcLinbc', source='sync_script')
            obj.delete()
        
        for offset in range(0, len(bc_ids), batch_size):
            batch_ids = bc_ids[offset:offset+batch_size]
            # --- Synchronisation des lignes pour ce batch de BC ---
            for bc_id in batch_ids:
                bc = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'read', [[bc_id]])[0]
                # Résolution des FK Odoo
                fournisseur_obj = None
                fournisseur_centre_obj = None
                depositaire_obj = None
                
                # Gestion robuste de la récupération du fournisseur
                fournisseur_val = bc.get('fournisseur', None)
                if isinstance(fournisseur_val, (list, tuple)) and fournisseur_val:
                    fournisseur_id = fournisseur_val[0]
                elif isinstance(fournisseur_val, int):
                    fournisseur_id = fournisseur_val
                else:
                    fournisseur_id = None
                
                if fournisseur_id:
                    fournisseur_obj = ScrapFournisseur.objects.filter(odoo_id=fournisseur_id).first()
                
                # Gestion robuste de la récupération du fournisseur_centre
                fournisseur_centre_val = bc.get('fournisseur_centre', None)
                if isinstance(fournisseur_centre_val, (list, tuple)) and fournisseur_centre_val:
                    fournisseur_centre_id = fournisseur_centre_val[0]
                elif isinstance(fournisseur_centre_val, int):
                    fournisseur_centre_id = fournisseur_centre_val
                else:
                    fournisseur_centre_id = None
                if fournisseur_centre_id:
                    fournisseur_centre_obj = ScrapFournisseurCentre.objects.filter(odoo_id=fournisseur_centre_id).first()
                
                # Gestion robuste du depositaire
                depositaire_val = bc.get('depositaire', None)
                if isinstance(depositaire_val, (list, tuple)) and depositaire_val:
                    depositaire_id = depositaire_val[0]
                elif isinstance(depositaire_val, int):
                    depositaire_id = depositaire_val
                else:
                    depositaire_id = None
                if depositaire_id:
                    depositaire_obj = ScrapUser.objects.filter(odoo_id=depositaire_id).first()
                old_obj = ScrapDimagazBC.objects.filter(odoo_id=bc['id']).first()
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
                    diff = compute_diff(old_obj, bc_obj) if not created else None
                    log_audit(bc_obj, 'created' if created else 'updated', changed_by='sync_BcLinbc', diff=diff, source='sync_script')
                    # Synchronisation des lignes associées à ce BC
                    line_search_domain = [('bc_id', '=', bc_id)]
                    line_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'search', [line_search_domain])
                    # Suppression des logs de debug détaillés (création/MAJ ligne, records, etc.)
                    pass  # Ici, on garde juste la logique métier, sans logs verbeux
                # --- Fin de synchronisation d'un BC ---
                # Log léger : nombre de lignes BC présentes
                nb_lines = ScrapDimagazBCLine.objects.filter(bc=bc_obj).count()
                self.stdout.write(f"BC {bc_obj.odoo_id}: {nb_lines} lignes synchronisées.")

        self.stdout.write(self.style.SUCCESS('Synchronisation terminée.'))
