import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
from django.db import transaction
from scrap_sga.models import ScrapUser
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
                ScrapUser.objects.update_or_create(
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
        self.stdout.write(self.style.SUCCESS('Synchronisation des utilisateurs terminée.'))
