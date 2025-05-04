import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from django.db import transaction
from scrap_sga.models import ScrapUser
from scrap_sga.utils_audit import log_audit, compute_diff, log_delete
from datetime import datetime
from django.utils import timezone
import datetime
from django.forms.models import model_to_dict
import pytz

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

def make_aware_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt
    return pytz.UTC.localize(dt)

def parse_odoo_datetime(dt_str):
    if not dt_str:
        return None
    dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    return make_aware_utc(dt)

class Command(BaseCommand):
    help = 'Synchronise les utilisateurs (dimagaz.user) depuis Odoo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Connexion à Odoo...'))
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            self.stdout.write(self.style.ERROR('Echec authentification Odoo'))
            return
        self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        user_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.user', 'search', [[]])
        self.stdout.write(f"{len(user_ids)} utilisateurs trouvés.")
        for user_id in user_ids:
            users = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.user', 'read', [[user_id]])
            if not users:
                continue
            u = users[0]
            with transaction.atomic():
                old_obj = ScrapUser.objects.filter(odoo_id=u['id']).first()
                obj, created = ScrapUser.objects.update_or_create(
                    odoo_id=u['id'],
                    defaults={
                        'name': u.get('name', ''),
                        'display_name': u.get('display_name', ''),
                        'username': u.get('username', ''),
                        'password': u.get('password', ''),
                        'sap_id': u.get('sap_id', ''),
                        'create_date': parse_odoo_datetime(u.get('create_date')),
                        'write_date': parse_odoo_datetime(u.get('write_date')),
                    }
                )
                diff = compute_diff(old_obj, obj) if not created else None
                log_audit(obj, 'created' if created else 'updated', changed_by='sync_user', diff=diff, source='sync_script')
        # Suppression des users locaux absents d'Odoo
        odoo_ids = set(user_ids)
        local_ids = set(ScrapUser.objects.values_list('odoo_id', flat=True))
        to_delete = local_ids - odoo_ids
        for del_id in to_delete:
            obj = ScrapUser.objects.get(odoo_id=del_id)
            log_delete(obj, changed_by='sync_user', source='sync_script')
            obj.delete()
        self.stdout.write(self.style.SUCCESS('Synchronisation des utilisateurs terminée.'))
