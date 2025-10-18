import csv
from django.core.management.base import BaseCommand
from main.models import Studio
from pathlib import Path


class Command(BaseCommand):
    help = 'Import or update studios from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing studios before importing',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing studios with new data from CSV',
        )

    def handle(self, *args, **options):
        # Path to CSV file
        csv_file = Path(__file__).resolve().parent.parent.parent.parent / 'DataSet - List Pilates _ Yoga Studio Jabodetabek (1).csv'
        
        if not csv_file.exists():
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file}'))
            return

        # Clear existing studios if --clear flag is used
        if options['clear']:
            Studio.objects.all().delete()
            self.stdout.write(self.style.WARNING('All existing studios have been deleted.'))

        # City mapping from CSV values to database values
        city_mapping = {
            'Bekasi': 'Bekasi',
            'Bogor': 'Bogor',
            'Depok': 'Depok',
            'Tangerang': 'Tangerang',
            'Jakarta': 'Jakarta',
            'Jakarta Barat': 'Jakarta',
            'Jakarta Pusat': 'Jakarta',
            'Jakarta Selatan': 'Jakarta',
            'Jakarta Timur': 'Jakarta',
            'Jakarta Utara': 'Jakarta',
        }

        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            # Skip the first two lines (header rows)
            next(file)
            next(file)
            
            csv_reader = csv.reader(file)
            
            for row in csv_reader:
                if len(row) < 5:  # Skip incomplete rows
                    continue
                    
                nama_studio = row[0].strip()
                wilayah = row[1].strip()
                area = row[2].strip()
                alamat = row[3].strip()
                nomor_telepon = row[4].strip()
                
                # Skip empty rows
                if not nama_studio or not wilayah:
                    continue
                
                # Map city name
                kota = city_mapping.get(wilayah)
                if not kota:
                    self.stdout.write(
                        self.style.WARNING(f'Unknown city: {wilayah} for studio {nama_studio}. Skipping.')
                    )
                    skipped_count += 1
                    continue
                
                # Check if studio already exists
                try:
                    existing_studio = Studio.objects.filter(nama_studio=nama_studio, kota=kota).first()
                    
                    if existing_studio:
                        if options['update']:
                            # Update existing studio
                            existing_studio.area = area
                            existing_studio.alamat = alamat
                            existing_studio.nomor_telepon = nomor_telepon
                            existing_studio.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'↻ Updated: {nama_studio} ({kota})')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'Studio "{nama_studio}" in {kota} already exists. Skipping.')
                            )
                            skipped_count += 1
                    else:
                        # Create new studio
                        Studio.objects.create(
                            nama_studio=nama_studio,
                            kota=kota,
                            area=area,
                            alamat=alamat,
                            nomor_telepon=nomor_telepon,
                        )
                        imported_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Imported: {nama_studio} ({kota})')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {nama_studio}: {str(e)}')
                    )
                    skipped_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== Import Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Successfully imported: {imported_count} studios'))
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated: {updated_count} studios'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} studios'))
