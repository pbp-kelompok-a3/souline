import csv
from django.core.management.base import BaseCommand
from studio.models import Studio

class Command(BaseCommand):
    help = 'Import studios from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # Skip first line
            reader = csv.DictReader(lines[1:], fieldnames=['Nama Studio', 'Wilayah Utama', 'Area Spesifik', 'Alamat Lengkap', 'Nomor Telepon'])
            for row in reader:
                nama_studio = row['Nama Studio'].strip()
                if not nama_studio:
                    continue
                kota = row['Wilayah Utama'].strip()
                area = row['Area Spesifik'].strip()
                if kota in ['Jakarta', 'Bogor', 'Depok', 'Tangerang', 'Bekasi']:
                    Studio.objects.get_or_create(
                        nama_studio=nama_studio,
                        defaults={'kota': kota, 'area': area, 'rating': 0.0}
                    )
                    self.stdout.write(self.style.SUCCESS(f'Imported {nama_studio}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped {nama_studio} - invalid kota'))
        self.stdout.write(self.style.SUCCESS('Import completed'))