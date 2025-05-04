import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from django.conf import settings
from scrap_sga.models import ScrapDimagazBC, ScrapDimagazBCLine, ScrapFournisseur, ScrapFournisseurCentre, ScrapUser, ScrapProduct, SyncState, SyncLog
from django.db import transaction
from datetime import datetime
import pytz
from django.utils import timezone
from scrap_sga.utils_audit import log_audit, compute_diff, log_delete
from django.forms.models import model_to_dict
import socket
import requests

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

def send_discord_bc_notification(bc_obj):
    webhook_url = os.environ.get('DISCORD_WEBHOOK_BC')
    if not webhook_url:
        print("Webhook Discord BC non défini")
        return
    ODOO_BASE_URL = os.environ.get('ODOO_URL')
    ODOO_BC_ACTION = os.environ.get('ODOO_BC_ACTION', '85')
    ODOO_MENU_ID = os.environ.get('ODOO_BC_MENU_ID', '69')
    record_url = f"{ODOO_BASE_URL}/web#id={bc_obj.odoo_id}&action={ODOO_BC_ACTION}&model=dimagaz.bc&view_type=form&cids=1&menu_id={ODOO_MENU_ID}"
    depositaire = bc_obj.depositaire.nom if bc_obj.depositaire and hasattr(bc_obj.depositaire, 'nom') else str(bc_obj.depositaire) if bc_obj.depositaire else "N/A"
    create_date = bc_obj.create_date
    maroc_tz = pytz.timezone('Africa/Casablanca')
    if create_date.tzinfo is None or create_date.tzinfo.utcoffset(create_date) is None:
        create_date = pytz.utc.localize(create_date)
    date_maroc = create_date.astimezone(maroc_tz)
    date_str = date_maroc.strftime('%d-%m-%Y %H:%M')
    message = (
        f"📦 **Nouvelle commande créée !**\n\n"
        f"> **Dépositaire** : `{depositaire}`\n"
        f"> **Numéro BC** : `{bc_obj.name}`\n"
        f"> **Date Création** : `{date_str}`\n"
        f"> [🔗 Voir dans ASG]({record_url}) _(connexion ASG requise)_"
    )
    try:
        requests.post(webhook_url, json={'content': message})
    except Exception as e:
        print(f"Erreur Discord BC : {e}")

class Command(BaseCommand):
    help = 'Synchronise les BC et lignes BC depuis Odoo vers la base locale (anti-doublon, upsert)'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=100, help='Taille du batch pour la synchro Odoo')
        parser.add_argument('--last', type=int, default=None, help='Limiter aux X derniers BC (et leurs lignes)')
        parser.add_argument('--name', type=str, default=None, help='Filtrer sur le champ name de dimagaz.bc')
        parser.add_argument('--date', type=int, default=None, help="Limiter aux BC créés ou modifiés dans les X dernières heures")
        parser.add_argument('--reset', action='store_true', help="Réinitialiser le curseur last_sync pour une synchro globale complète")

    def handle(self, *args, **options):
        # Timeout XML-RPC global
        socket.setdefaulttimeout(30)

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

        # Gestion du last_sync incrémental intelligente
        name = options['name']
        date_hours = options.get('date')
        reset = options.get('reset')
        if name or date_hours:
            sync_key = f'bclinbc_custom_{name or date_hours}'
            update_last_sync = False
        else:
            sync_key = 'bclinbc'
            update_last_sync = True
        now_sync = timezone.now()
        last_sync = None
        syncstate, _ = SyncState.objects.get_or_create(name=sync_key)
        # Ajout du reset last_sync si demandé
        if reset and update_last_sync:
            syncstate.last_sync = None
            syncstate.save()
            self.stdout.write(self.style.WARNING("Curseur last_sync réinitialisé : synchronisation globale forcée."))
        if syncstate.last_sync:
            last_sync = syncstate.last_sync
        else:
            # Date très ancienne par défaut
            last_sync = datetime(2000, 1, 1, tzinfo=pytz.utc)
        self.stdout.write(self.style.NOTICE(f"Synchronisation incrémentale depuis {last_sync} (jusqu'à {now_sync})"))
        batch_size = options['batch_size']
        last = options['last']
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

        # Gestion du lock de synchronisation
        if syncstate.is_syncing:
            self.stdout.write(self.style.ERROR("Synchronisation déjà en cours (is_syncing=True). Abandon."))
            return
        syncstate.is_syncing = True
        syncstate.save()
        log_obj = SyncLog.objects.create(sync_type='bclinbc', status='error', bc_synced=0, line_synced=0)

        try:
            # Recherche incrémentale des BC Odoo
            bc_search_domain = [('write_date', '>', last_sync.strftime('%Y-%m-%d %H:%M:%S'))]
            if name:
                bc_search_domain.append(('name', '=', name))
            if date_hours:
                since = timezone.now() - timezone.timedelta(hours=date_hours)
                bc_search_domain.append(('write_date', '>=', since.strftime('%Y-%m-%d %H:%M:%S')))
            fields_bc = [
                'id', 'name', 'fullname', 'bc_date', 'bl_date', 'fournisseur', 'fournisseur_centre', 'depositaire', 'montant_paye', 'done', 'sap', 'confirmed', 'remise', 'tva', 'ht', 'ttc', 'bc_type', 'state', 'terminated', 'verify_state', 'qty_retenue', 'paye_par', 'bl_number', 'solde', 'non_conforme', 'version', 'prefix', 'source', 'product_type', 'display_name', 'create_date', 'write_date',
                'bc_lines'  # <-- AJOUT pour synchroniser les lignes BC
            ]
            fields_line = ['id', 'bc_id', 'product', 'qty', 'qty_vide', 'qty_retenue', 'qty_defect', 'prix', 'subtotal', 'bc_date', 'create_date', 'write_date']
            total_synced = 0
            total_lines = 0
            for offset in range(0, 100000000, batch_size):  # boucle infinie, break si moins que batch_size
                bcs = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'search_read',
                    [bc_search_domain],
                    {'fields': fields_bc, 'limit': batch_size, 'offset': offset, 'order': 'id asc'}
                )
                if not bcs:
                    break
                for bc in bcs:
                    try:
                        with transaction.atomic():
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
                                    'version': bc.get('version', ''),
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
                            if created:
                                send_discord_bc_notification(bc_obj)
                            # Synchronisation des lignes associées à ce BC
                            line_ids = bc.get('bc_lines', [])
                            if line_ids:
                                line_records = models.execute_kw(
                                    ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'read', [line_ids], {'fields': fields_line}
                                )
                                for line in line_records:
                                    product_obj = None
                                    product_id = line.get('product', [None])[0]
                                    product_name = None
                                    
                                    if product_id:
                                        product_obj = ScrapProduct.objects.filter(odoo_id=product_id).first()
                                        if product_obj:
                                            product_name = product_obj.name
                                    
                                    old_line = ScrapDimagazBCLine.objects.filter(odoo_id=line['id']).first()
                                    obj, created = ScrapDimagazBCLine.objects.update_or_create(
                                        odoo_id=line['id'],
                                        defaults={
                                            'bc': bc_obj,
                                            'product': product_obj,
                                            'product_name': product_name,  # Ajout du nom du produit depuis l'objet ScrapProduct
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
                                    diff_line = compute_diff(old_line, obj) if not created else None
                                    log_audit(obj, 'created' if created else 'updated', changed_by='sync_BcLinbc', diff=diff_line, source='sync_script')
                            # --- Suppression des lignes BC locales absentes d'Odoo pour ce BC (sans filtre date) ---
                            all_line_ids = set(models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'search', [[('bc_id', '=', bc['id'])]]))
                            local_line_ids = set(ScrapDimagazBCLine.objects.filter(bc=bc_obj).values_list('odoo_id', flat=True))
                            to_delete_line = local_line_ids - all_line_ids
                            for del_id in to_delete_line:
                                obj = ScrapDimagazBCLine.objects.get(odoo_id=del_id)
                                log_delete(obj, changed_by='sync_BcLinbc', source='sync_script')
                                obj.delete()

                            # --- Fin de synchronisation d'un BC ---
                            # Log léger : nombre de lignes BC présentes
                            nb_lines = ScrapDimagazBCLine.objects.filter(bc=bc_obj).count()
                            self.stdout.write(f"BC {bc_obj.odoo_id}: {nb_lines} lignes synchronisées.")
                            total_synced += 1
                            total_lines += nb_lines
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Erreur sur BC {bc.get('id')}: {e}"))
                        continue

            if update_last_sync:
                syncstate.last_sync = now_sync
                syncstate.save()
            log_obj.status = 'success'
            log_obj.details = f"{total_synced} BC synchronisés, {total_lines} lignes synchronisées."
            log_obj.bc_synced = total_synced
            log_obj.line_synced = total_lines
            self.stdout.write(self.style.SUCCESS(f"Synchronisation incrémentale terminée. BC synchronisés: {total_synced}, lignes: {total_lines}"))
        except Exception as err:
            log_obj.status = 'error'
            log_obj.error_message = str(err)
            self.stdout.write(self.style.ERROR(f"Erreur critique lors de la synchronisation : {err}"))
        finally:
            syncstate.is_syncing = False
            syncstate.save()
            log_obj.end_time = timezone.now()
            log_obj.save()
