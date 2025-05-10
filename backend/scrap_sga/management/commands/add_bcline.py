import os
from dotenv import load_dotenv
load_dotenv()
from django.core.management.base import BaseCommand, CommandError
import xmlrpc.client
import json
from datetime import datetime

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

class Command(BaseCommand):
    help = "Ajoute une ligne à un BC Odoo (dimagaz.bc.line), met à jour montant_paye et ttc du BC, puis décrémente le solde du dépositaire dans dimagaz.user. Ne touche pas à la BDD locale."

    def add_arguments(self, parser):
        parser.add_argument('--json_line', type=str, required=True, help='Chemin du fichier JSON contenant la structure de la ligne à ajouter')

    def handle(self, *args, **options):
        json_path = options['json_line']
        with open(json_path, 'r', encoding='utf-8') as f:
            line_data = json.load(f)
        vals = {
            'bc_id': line_data['bc_id'][0],
            'product': line_data['product'][0],
            'qty': line_data.get('qty', 0),
            'qty_vide': line_data.get('qty_vide', 0),
            'qty_retenue': line_data.get('qty_retenue', 0),
            'qty_defect': line_data.get('qty_defect', 0),
            'prix': line_data.get('prix', 0),
            'subtotal': line_data.get('subtotal', 0),
        }
        if 'bc_date' in line_data and line_data['bc_date']:
            vals['bc_date'] = line_data['bc_date']
        self.stdout.write(self.style.NOTICE(f"Connexion à Odoo pour ajout dimagaz.bc.line sur BC id={vals['bc_id']}..."))
        try:
            common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
            if not uid:
                raise CommandError('Echec authentification Odoo')
            models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
            # 1. Création de la ligne
            new_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'dimagaz.bc.line', 'create', [vals]
            )
            self.stdout.write(self.style.SUCCESS(f"Ligne créée dans Odoo avec id={new_id}"))
            created_line = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'dimagaz.bc.line', 'read', [[new_id]]
            )[0]
            self.stdout.write(json.dumps(created_line, indent=2, ensure_ascii=False, default=str))
            # 2. Mise à jour du BC parent
            bc_id = vals['bc_id']
            subtotal = vals['subtotal']
            bc = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'dimagaz.bc', 'read', [[bc_id]]
            )[0]
            montant_paye = bc.get('montant_paye', 0) or 0
            ttc = bc.get('ttc', 0) or 0
            new_montant_paye = montant_paye + subtotal
            new_ttc = ttc + subtotal
            update_vals = {
                'montant_paye': new_montant_paye,
                'ttc': new_ttc
            }
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'dimagaz.bc', 'write', [[bc_id], update_vals]
            )
            self.stdout.write(self.style.SUCCESS(f"BC id={bc_id} mis à jour : montant_paye={new_montant_paye}, ttc={new_ttc}"))
            # 3. Décrément du solde du dépositaire
            depositaire = bc.get('depositaire')
            if not depositaire or not isinstance(depositaire, list) or not depositaire[0]:
                self.stdout.write(self.style.WARNING("Pas de dépositaire défini sur ce BC, solde non modifié."))
            else:
                depositaire_id = depositaire[0]
                user = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'dimagaz.user', 'read', [[depositaire_id]]
                )[0]
                solde = user.get('solde', 0) or 0
                new_solde = solde - subtotal
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'dimagaz.user', 'write', [[depositaire_id], {'solde': new_solde}]
                )
                self.stdout.write(self.style.SUCCESS(f"Solde du dépositaire id={depositaire_id} mis à jour : {solde} -> {new_solde}"))
        except Exception as e:
            raise CommandError(f"Erreur lors de la création/mise à jour dans Odoo : {e}")
