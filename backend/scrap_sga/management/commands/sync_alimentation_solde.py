import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from scrap_sga.models import AlimentationSolde, SyncLog, SyncState
from django.utils import timezone
from datetime import datetime
import requests
import socket
from django.db import transaction
import pytz

def parse_odoo_datetime(dt_str):
    if not dt_str or dt_str is False:
        return None
    return timezone.make_aware(datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S'))

def safe_str(val):
    if val is False or val is None:
        return None
    return str(val)

def make_aware_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt
    return pytz.UTC.localize(dt)

def send_discord_notification(obj):
    webhook_url = os.environ.get('DISCORD_WEBHOOK_SOLDE')
    if not webhook_url:
        print("Webhook Discord non défini")
        return
    try:
        ODOO_BASE_URL = os.environ.get('ODOO_URL')
        ODOO_ACTION = os.environ.get('ODOO_ALIM_ACTION', '333')
        ODOO_MENU_ID = os.environ.get('ODOO_ALIM_MENU_ID', '69')
        record_url = f"{ODOO_BASE_URL}/web#id={obj.odoo_id}&action={ODOO_ACTION}&model=alimenter.solde&view_type=form&cids=1&menu_id={ODOO_MENU_ID}"

        maroc_tz = pytz.timezone('Africa/Casablanca')
        # Si la date n'est pas aware, la rendre UTC avant conversion
        create_date = obj.create_date
        if create_date.tzinfo is None or create_date.tzinfo.utcoffset(create_date) is None:
            create_date = make_aware_utc(create_date)
        date_maroc = create_date.astimezone(maroc_tz)
        date_str = date_maroc.strftime('%d-%m-%Y %H:%M')

        message = (
            "💸 **Nouvelle alimentation détectée !**\n\n"
            f"> **Dépositaire** : `{obj.display_name}`\n"
            f"> **N° Alimentation** : `{obj.reference_no}`\n"
            f"> **Date Création** : `{date_str}`\n"
            f"> [🔗 Voir dans ASG]({record_url}) _(Connexion ASG requise)_"
        )
        requests.post(webhook_url, json={'content': message})
    except Exception as e:
        print(f"Erreur Discord : {e}")

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK_SOLDE')

class Command(BaseCommand):
    help = "Synchronise la table Odoo alimenter.solde vers AlimentationSolde, et notifie Discord à chaque nouvelle alimentation. Audit SyncLog/SyncState inclus."

    def handle(self, *args, **options):
        socket.setdefaulttimeout(30)
        sync_type = 'alimentation_solde'
        sync_log = SyncLog.objects.create(sync_type=sync_type, status='error', details='', error_message='')
        sync_state, _ = SyncState.objects.get_or_create(name=sync_type)
        sync_state.is_syncing = True
        sync_state.save()
        start_time = timezone.now()
        try:
            self.stdout.write(self.style.NOTICE('Connexion à Odoo...'))
            common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
            if not uid:
                raise Exception('Echec authentification Odoo')
            self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
            models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

            # Détermination de la date de dernière sync
            last_sync = sync_state.last_sync
            domain = []
            if last_sync:
                domain = ['|', ('create_date', '>', last_sync.strftime('%Y-%m-%d %H:%M:%S')), ('write_date', '>', last_sync.strftime('%Y-%m-%d %H:%M:%S'))]
                self.stdout.write(self.style.NOTICE(f"Sync incrémentale depuis {last_sync}"))
            else:
                self.stdout.write(self.style.NOTICE("Sync complète (premier lancement ou reset)"))
            solde_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'alimenter.solde', 'search', [domain]
            )
            self.stdout.write(f"{len(solde_ids)} alimentations à traiter depuis Odoo.")

            new_count = 0
            skipped = 0
            for batch_start in range(0, len(solde_ids), 100):
                batch_ids = solde_ids[batch_start:batch_start+100]
                records = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'alimenter.solde', 'read', [batch_ids]
                )
                for solde in records:
                    if AlimentationSolde.objects.filter(odoo_id=solde['id']).exists():
                        continue  # déjà importé
                    # Skip si pas de client (name mal formé)
                    if not solde.get('name') or not isinstance(solde['name'], list) or len(solde['name']) < 2:
                        self.stdout.write(self.style.WARNING(
                            f"[SKIP] Odoo id={solde.get('id')} ref={solde.get('reference_no')} : champ name invalide ({solde.get('name')})"
                        ))
                        skipped += 1
                        continue
                    with transaction.atomic():
                        obj = AlimentationSolde(
                            odoo_id=solde['id'],
                            client_odoo_id=solde['name'][0],
                            client_nom=solde['name'][1],
                            solde=solde['solde'],
                            state=solde['state'],
                            date_done=parse_odoo_datetime(solde['date_done']),
                            comment=safe_str(solde['comment']),
                            avoir=safe_str(solde['avoir']),
                            reference_no=solde['reference_no'],
                            date_creation=parse_odoo_datetime(solde['date_creation']),
                            date_refus=parse_odoo_datetime(solde['date_refus']),
                            refus_raisons=safe_str(solde['refus_raisons']),
                            source=solde['source'],
                            created_by=safe_str(solde['created_by']),
                            display_name=solde['display_name'],
                            create_date=parse_odoo_datetime(solde['create_date']),
                            write_date=parse_odoo_datetime(solde['write_date'])
                        )
                        obj.save()
                        new_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"[NOUVEAU] Odoo id={obj.odoo_id} ref={obj.reference_no} client={obj.client_nom} montant={obj.solde}"
                        ))
                        send_discord_notification(obj)
            sync_log.status = 'success'
            sync_log.details = f"{new_count} nouvelles alimentations importées et notifiées. {skipped} ignorées."
            sync_state.last_sync = timezone.now()
        except Exception as e:
            sync_log.status = 'error'
            sync_log.error_message = str(e)
            self.stdout.write(self.style.ERROR(f"[SYNC FAIL] {e}"))
        finally:
            sync_log.end_time = timezone.now()
            sync_log.save()
            sync_state.is_syncing = False
            sync_state.save()
            self.stdout.write(self.style.SUCCESS(f"Synchronisation terminée. Statut: {sync_log.status}. Détail: {sync_log.details}"))
