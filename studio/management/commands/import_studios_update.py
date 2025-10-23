import csv
import time
import googlemaps
from django.core.management.base import BaseCommand
from django.conf import settings
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
        # Initialize Google Maps client
        api_key = settings.GMAPS_API_KEY
        if not api_key:
            self.stdout.write(self.style.ERROR('Google Maps API key not found in settings'))
            return
        
        gmaps = googlemaps.Client(key=api_key)
        
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
                            # Check if both thumbnail and gmaps_link are already populated
                            if existing_studio.thumbnail and existing_studio.gmaps_link:
                                self.stdout.write(
                                    self.style.WARNING(f'Studio "{nama_studio}" in {kota} already has complete data. Skipping.')
                                )
                                skipped_count += 1
                                continue
                            
                            # Update existing studio
                            existing_studio.area = area
                            existing_studio.alamat = alamat
                            existing_studio.nomor_telepon = nomor_telepon
                            
                            # Fetch Google Places data only if missing
                            if not existing_studio.thumbnail or not existing_studio.gmaps_link:
                                thumbnail_url, gmaps_link = self.fetch_place_data(
                                    gmaps, api_key, nama_studio, kota, area
                                )
                                existing_studio.thumbnail = thumbnail_url
                                existing_studio.gmaps_link = gmaps_link
                                time.sleep(1)  # Rate limiting
                            
                            existing_studio.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'[UPDATE] Updated: {nama_studio} ({kota})')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'Studio "{nama_studio}" in {kota} already exists. Skipping.')
                            )
                            skipped_count += 1
                    else:
                        # Fetch Google Places data for new studio
                        thumbnail_url, gmaps_link = self.fetch_place_data(
                            gmaps, api_key, nama_studio, kota, area
                        )
                        time.sleep(1)  # Rate limiting
                        
                        # Create new studio
                        Studio.objects.create(
                            nama_studio=nama_studio,
                            kota=kota,
                            area=area,
                            alamat=alamat,
                            nomor_telepon=nomor_telepon,
                            thumbnail=thumbnail_url,
                            gmaps_link=gmaps_link,
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
    
    def fetch_place_data(self, gmaps, api_key, nama_studio, kota, area):
        """
        Fetch thumbnail and Google Maps link for a studio using Google Places API
        """
        placeholder_image = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
        
        try:
            # Search query for better accuracy
            query = f"{nama_studio} pilates yoga {kota} Indonesia"
            
            # Find place using Places API
            places_result = gmaps.places(query=query)
            
            if places_result['status'] == 'OK' and places_result['results']:
                place = places_result['results'][0]
                place_id = place.get('place_id')
                
                thumbnail_url = placeholder_image
                gmaps_link = f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"
                
                # Get photo from initial result
                if 'photos' in place and place['photos']:
                    photo_reference = place['photos'][0]['photo_reference']
                    # Construct photo URL (max width 400px for thumbnails)
                    thumbnail_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={api_key}"
                
                # Get place details for Google Maps URL
                place_details = gmaps.place(place_id=place_id, fields=['url'])
                
                # Get Google Maps link
                if place_details['status'] == 'OK' and 'url' in place_details['result']:
                    gmaps_link = place_details['result']['url']
                
                self.stdout.write(
                    self.style.SUCCESS(f'  -> Found place data for {nama_studio}')
                )
                return thumbnail_url, gmaps_link
            else:
                self.stdout.write(
                    self.style.WARNING(f'  -> Place not found for {nama_studio}, using placeholder')
                )
                return placeholder_image, f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  -> Error fetching place data for {nama_studio}: {str(e)}')
            )
            query = f"{nama_studio} {kota} Indonesia"
            return placeholder_image, f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"
