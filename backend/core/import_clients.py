import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Client, User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Importe les clients depuis un fichier Excel (XLSX ou CSV)'

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Chemin du fichier Excel (.xlsx) ou CSV à importer')
        parser.add_argument('--user', type=str, help='Nom d\'utilisateur pour l\'audit (optionnel)')

    def handle(self, *args, **options):
        filepath = options['filepath']
        username = options.get('user')
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Utilisateur {username} introuvable, l'audit sera anonyme."))
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        created, updated = 0, 0
        for _, row in df.iterrows():
            client, created_flag = Client.objects.update_or_create(
                sap_id=row['sap_id'],
                defaults={
                    'nom_client': row.get('nom_client', ''),
                    'telephone': row.get('telephone', ''),
                    'telephone2': row.get('telephone2', ''),
                    'telephone3': row.get('telephone3', ''),
                    'langue': row.get('langue', 'francais'),
                    'statut_general': row.get('statut_general', 'actif'),
                    'notification_client': bool(row.get('notification_client', False)),
                    'date_notification': row.get('date_notification') or None,
                    'a_demande_aide': bool(row.get('a_demande_aide', False)),
                    'nature_aide': row.get('nature_aide', ''),
                    'app_installee': bool(row.get('app_installee', False)),
                    'maj_app': row.get('maj_app', ''),
                    'commentaire_agent': row.get('commentaire_agent', ''),
                    'segment_client': row.get('segment_client', ''),
                    'region': row.get('region', ''),
                    'ville': row.get('ville', ''),
                    'canal_contact': row.get('canal_contact', ''),
                    'relance_planifiee': bool(row.get('relance_planifiee', False)),
                    'cree_par_user': user,
                    'modifie_par_user': user,
                }
            )
            # Pour le moteur métier : indique l'utilisateur courant
            client._current_user = user
            client.save()
            if created_flag:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Import terminé : {created} créés, {updated} mis à jour."))
