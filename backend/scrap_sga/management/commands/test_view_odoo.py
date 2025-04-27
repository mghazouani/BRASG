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
    help = 'Dump un enregistrement de dimagaz.bc (sélectionné par name), ses lignes, le user dépositaire ET les produits en JSON.'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Nom (name) du BC à exporter')
        parser.add_argument('--product-id', type=int, help='ID Odoo du produit à visualiser (optionnel)')

    def handle(self, *args, **options):
        name = options.get('name')
        product_id = options.get('product_id')
        self.stdout.write(self.style.NOTICE('Connexion à Odoo...'))
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            self.stdout.write(self.style.ERROR('Echec authentification Odoo'))
            return
        self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        # Recherche du BC par name
        if name:
            bc_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'search', [[('name', '=', name)]], {'limit': 1})
        else:
            bc_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'search', [[]], {'limit': 1})
        if not bc_ids:
            self.stdout.write('Aucun BC trouvé.')
            return
        bc = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc', 'read', [bc_ids])[0]

        # Toutes les lignes liées à ce BC
        line_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'search', [[('bc_id', '=', bc['id'])]])
        lines = []
        if line_ids:
            lines = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.bc.line', 'read', [line_ids])

        # User dépositaire (dimagaz.user.id = bc['depositaire'][0])
        user = None
        if bc.get('depositaire') and isinstance(bc['depositaire'], list) and bc['depositaire']:
            user_id = bc['depositaire'][0]
            user_records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.user', 'read', [[user_id]])
            if user_records:
                user = user_records[0]

        # Produits :
        products = []
        if product_id:
            # Un produit spécifique
            prod = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.product', 'read', [[product_id]])
            if prod:
                products = prod
        else:
            # Tous les produits (limite à 10 pour test)
            product_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.product', 'search', [[]], {'limit': 10})
            if product_ids:
                products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'dimagaz.product', 'read', [product_ids])

        # Dump JSON dans un fichier
        data = {
            'dimagaz.bc': bc,
            'dimagaz.bc.line': lines,
            'dimagaz.user': user,
            'dimagaz.product': products,
        }
        out_path = f"odoo_bc_{name or 'sample'}_products.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.stdout.write(self.style.SUCCESS(f'Données exportées dans {out_path}'))
