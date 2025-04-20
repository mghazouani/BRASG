import csv
import os
from django.core.management.base import BaseCommand, CommandError
from core.models import Ville


class Command(BaseCommand):
    help = 'Importe les villes depuis un fichier CSV (colonnes: ville,latitude,longitude,pays,iso2,région)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Chemin vers le fichier CSV des villes')

    def handle(self, *args, **options):
        path = options['csv_file']
        if not os.path.exists(path):
            raise CommandError(f"Le fichier {path} n'existe pas.")
        created = 0
        updated = 0
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nom = row.get('ville', '').strip()
                try:
                    latitude = float(row.get('latitude', 0) or 0)
                    longitude = float(row.get('longitude', 0) or 0)
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Valeurs invalides en lat/long pour {nom}"))
                    continue
                pays = row.get('pays', '').strip()
                iso2 = row.get('iso2', '').strip()
                region = row.get('région', row.get('region', '')).strip()
                ville_obj, created_flag = Ville.objects.update_or_create(
                    nom=nom,
                    defaults={
                        'latitude': latitude,
                        'longitude': longitude,
                        'pays': pays,
                        'iso2': iso2,
                        'region': region,
                    }
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f"Import terminé : {created} créées, {updated} mises à jour."))
