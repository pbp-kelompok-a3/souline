import csv
import time
import googlemaps
import requests
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from studio.models import Studio
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
        parser.add_argument(
            '--update-images',
            action='store_true',
            help='Update images for all existing studios',
        )

    def handle(self, *args, **options):
        # Initialize Google Maps client
        api_key = settings.GMAPS_API_KEY
        if not api_key:
            self.stdout.write(self.style.ERROR('Google Maps API key not found in settings'))
            return
        
        gmaps = googlemaps.Client(key=api_key)
        
        if options['update_images']:
            self.stdout.write('Updating images for all studios...')
            studios = Studio.objects.all()
            count = studios.count()
            
            for i, studio in enumerate(studios, 1):
                self.stdout.write(f'Processing {i}/{count}: {studio.nama_studio}')
                
                # Clear thumbnail
                studio.thumbnail = None
                
                try:
                    thumbnail_url, _, rating = self.fetch_place_data(
                        gmaps, api_key, studio.nama_studio, studio.kota, studio.area
                    )
                    studio.thumbnail = thumbnail_url
                    studio.rating = rating
                    studio.save()
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating {studio.nama_studio}: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS('Finished updating all studio images.'))
            return

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
                                thumbnail_url, gmaps_link, rating = self.fetch_place_data(
                                    gmaps, api_key, nama_studio, kota, area
                                )
                                existing_studio.thumbnail = thumbnail_url
                                existing_studio.gmaps_link = gmaps_link
                                existing_studio.rating = rating
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
                        thumbnail_url, gmaps_link, rating = self.fetch_place_data(
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
                            rating=rating,
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
        Fetch thumbnail, Google Maps link, and rating for a studio using Google Places API
        """
        placeholder_image = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
        rating = 5.0
        
        try:
            # Search query for better accuracy
            query = f"{nama_studio} pilates yoga {kota} Indonesia"
            
            # Find place using Places API
            places_result = gmaps.places(query=query)
            
            if places_result['status'] == 'OK' and places_result['results']:
                place = places_result['results'][0]
                place_id = place.get('place_id')
                rating = place.get('rating', 5.0)
                
                thumbnail_url = placeholder_image
                gmaps_link = f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"
                
                # Get photo from initial result
                if 'photos' in place and place['photos']:
                    photo_reference = place['photos'][0]['photo_reference']
                    # Construct photo URL to download the image
                    photo_api_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={api_key}"
                    
                    # Download the image and convert to a hosted URL (not API URL)
                    try:
                        response = requests.get(photo_api_url, timeout=10)
                        if response.status_code == 200:
                            # Use the final redirected URL (Google's CDN URL without API key)
                            thumbnail_url = response.url
                            self.stdout.write(self.style.SUCCESS(f'    -> Downloaded photo from Google CDN'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'    -> Failed to download photo: {str(e)}'))
                
                # Get place details for Google Maps URL
                place_details = gmaps.place(place_id=place_id, fields=['url'])
                
                # Get Google Maps link
                if place_details['status'] == 'OK' and 'url' in place_details['result']:
                    gmaps_link = place_details['result']['url']
                
                self.stdout.write(
                    self.style.SUCCESS(f'  -> Found place data for {nama_studio} (Rating: {rating})')
                )
                return thumbnail_url, gmaps_link, rating
            else:
                self.stdout.write(
                    self.style.WARNING(f'  -> Place not found for {nama_studio}, using placeholder')
                )
                return placeholder_image, f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}", rating
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  -> Error fetching place data for {nama_studio}: {str(e)}')
            )
            query = f"{nama_studio} {kota} Indonesia"
            return placeholder_image, f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}", rating
