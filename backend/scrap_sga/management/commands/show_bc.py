from django.core.management.base import BaseCommand, CommandError
import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
import json

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

class Command(BaseCommand):
    help = "Affiche le contenu détaillé d'un BC Odoo (dimagaz.bc.name) et toutes ses lignes, tous champs inclus. Sauvegarde dans un fichier JSON."

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Nom du BC (dimagaz.bc.name) dans Odoo')

    def handle(self, *args, **options):
        name = options['name']
        self.stdout.write(self.style.NOTICE(f"Connexion à Odoo pour rechercher dimagaz.bc.name = '{name}'..."))
        try:
            common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
            if not uid:
                raise CommandError('Echec authentification Odoo')
            models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

            bc_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'dimagaz.bc', 'search', [[('name', '=', name)]], {'limit': 1}
            )
            if not bc_ids:
                raise CommandError(f"Aucun BC trouvé dans Odoo avec name='{name}'")
            bc_id = bc_ids[0]
            bc_records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'dimagaz.bc', 'read', [bc_ids]
            )
            bc = bc_records[0]
            self.stdout.write(self.style.NOTICE("\n=== Bon de Commande (Odoo dimagaz.bc) ==="))
            self.stdout.write(json.dumps(bc, indent=2, ensure_ascii=False, default=str))

            # Récupérer toutes les lignes de ce BC
            line_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'dimagaz.bc.line', 'search', [[('bc_id', '=', bc_id)]]
            )
            lines = []
            if not line_ids:
                self.stdout.write(self.style.WARNING("Aucune ligne de commande pour ce BC dans Odoo."))
            else:
                lines = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'dimagaz.bc.line', 'read', [line_ids]
                )
                self.stdout.write(self.style.NOTICE(f"\n=== Lignes de Commande Odoo ({len(lines)}) ==="))
                for l in lines:
                    self.stdout.write(json.dumps(l, indent=2, ensure_ascii=False, default=str))

            # Sauvegarde dans un fichier
            out_path = f"bcodoo_{name}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'bc': bc, 'lines': lines}, f, indent=2, ensure_ascii=False, default=str)
            self.stdout.write(self.style.SUCCESS(f"\nExporté dans {out_path}"))
        except Exception as e:
            raise CommandError(f"Erreur lors de la lecture Odoo : {e}")
