import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand
import json

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

class Command(BaseCommand):
    help = "Affiche un alimenter.solde par reference_no (Odoo) et l'exporte en JSON."

    def add_arguments(self, parser):
        # Le paramètre reference_no est utilisé pour filtrer les objets alimenter.solde
        parser.add_argument('--reference_no', type=str, required=True, help="reference_no Odoo de l'alimenter.solde à afficher")

    def handle(self, *args, **options):
        reference_no = options.get('reference_no')
        self.stdout.write(self.style.NOTICE('Connexion à Odoo...'))
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            self.stdout.write(self.style.ERROR('Echec authentification Odoo'))
            return
        self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        # --- Les lignes suivantes sont à décommenter pour interroger le modèle alimenter.solde ---
        # solde_ids = models.execute_kw(
        #     ODOO_DB, uid, ODOO_PASSWORD,
        #     'alimenter.solde', 'search', [[('reference_no', '=', reference_no)]], {'limit': 1}
        # )
        # if not solde_ids:
        #     self.stdout.write(f'Aucun alimenter.solde trouvé pour reference_no={reference_no}.')
        #     return
        # solde_records = models.execute_kw(
        #     ODOO_DB, uid, ODOO_PASSWORD,
        #     'alimenter.solde', 'read', [solde_ids]
        # )
        # solde = solde_records[0]
        # # Affichage console
        # self.stdout.write(json.dumps(solde, indent=2, ensure_ascii=False))
        # # Dump JSON dans un fichier
        # out_path = f"odoo_alimenter_solde_{reference_no}.json"
        # with open(out_path, 'w', encoding='utf-8') as f:
        #     json.dump(solde, f, indent=2, ensure_ascii=False)
        # self.stdout.write(self.style.SUCCESS(f'Données exportées dans {out_path}'))
