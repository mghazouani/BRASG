import os
from dotenv import load_dotenv
load_dotenv()
import xmlrpc.client
from django.core.management.base import BaseCommand, CommandError

ODOO_URL = os.environ.get('ODOO_URL')
ODOO_DB = os.environ.get('ODOO_DB')
ODOO_USER = os.environ.get('ODOO_USER')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

class Command(BaseCommand):
    help = "Modifie les champs sap_id, solde et plafond_credit d'un ou plusieurs utilisateurs dimagaz.user (Odoo distant)."

    def add_arguments(self, parser):
        parser.add_argument('--odoo_id', type=int, help='ID Odoo de l\'utilisateur (dimagaz.user)')
        parser.add_argument('--username', type=str, help='Nom d\'utilisateur (facultatif, alternatif à odoo_id)')
        parser.add_argument('--name', type=str, help='Nom complet (name) de l\'utilisateur (alternatif)')
        parser.add_argument('--csv', type=str, help='Chemin d\'un fichier CSV contenant des noms (name) séparés par virgule')
        parser.add_argument('--sap_id', type=str, help='Nouveau SAP ID')
        parser.add_argument('--solde', type=float, help='Nouveau solde (float)')
        parser.add_argument('--plafond_credit', type=float, help='Nouveau plafond crédit (float)')

    def handle(self, *args, **options):
        odoo_id = options.get('odoo_id')
        username = options.get('username')
        name = options.get('name')
        csv_path = options.get('csv')
        sap_id = options.get('sap_id')
        solde = options.get('solde')
        plafond_credit = options.get('plafond_credit')
        self.stdout.write(self.style.NOTICE('Connexion à Odoo distant...'))
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        if not uid:
            raise CommandError('Echec authentification Odoo')
        self.stdout.write(self.style.SUCCESS(f"Connecté à Odoo UID={uid}"))
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        # Mode batch si --csv fourni
        names = []
        if csv_path:
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    names = [n.strip() for n in content.split(',') if n.strip()]
            except Exception as e:
                raise CommandError(f"Erreur lors de la lecture du fichier CSV : {e}")
            if not names:
                raise CommandError("Le fichier CSV ne contient aucun nom.")
        elif name:
            names = [name]
        elif odoo_id or username:
            names = [None]  # On traitera par odoo_id ou username uniquement
        else:
            raise CommandError('Vous devez fournir --odoo_id, --username, --name ou --csv')

        # Fonction pour modifier un utilisateur
        def update_user(name=None):
            domain = []
            if odoo_id:
                domain.append(('id', '=', odoo_id))
            elif username:
                domain.append(('login', '=', username))
            elif name:
                domain.append(('name', '=', name))
            else:
                return (False, 'Aucun critère fourni')
            try:
                user_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'dimagaz.user', 'search', [domain], {'limit': 1}
                )
                if not user_ids:
                    return (False, f"Aucun utilisateur trouvé pour {domain}")
                user_id = user_ids[0]
                vals = {}
                if sap_id is not None:
                    vals['sap_id'] = sap_id
                if solde is not None:
                    vals['solde'] = solde
                if plafond_credit is not None:
                    vals['plafond_credit'] = plafond_credit
                if not vals:
                    return (False, 'Aucun champ à modifier (--sap_id, --solde, --plafond_credit) fourni !')
                result = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'dimagaz.user', 'write', [[user_id], vals]
                )
                if result:
                    return (True, f"OK (id={user_id}) : {', '.join([f'{k}={v}' for k,v in vals.items()])}")
                else:
                    return (False, f"La modification a échoué (id={user_id})")
            except Exception as e:
                return (False, f"Erreur : {e}")

        # Traitement batch ou unitaire
        for n in names:
            cible = f"name='{n}'" if n else (f"odoo_id={odoo_id}" if odoo_id else f"username='{username}'")
            ok, msg = update_user(n)
            if ok:
                self.stdout.write(self.style.SUCCESS(f"[SUCCÈS] {cible} => {msg}"))
            else:
                self.stdout.write(self.style.ERROR(f"[ERREUR] {cible} => {msg}"))
