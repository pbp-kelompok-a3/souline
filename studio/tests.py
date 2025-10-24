from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from studio.models import Studio, KOTA_CHOICES
from studio.forms import StudioForm
from users.models import UserProfile
import uuid
import json

class StudioModelTest(TestCase):
    # Test case untuk models Studio
    
    def setUp(self):
        # Set up test data
        self.studio = Studio.objects.create(
            nama_studio="Test Yoga Studio",
            thumbnail="https://example.com/image.jpg",
            kota="Jakarta",
            area="Menteng",
            alamat="Jl. Test No. 123",
            gmaps_link="https://maps.google.com/test",
            nomor_telepon="081234567890"
        )
    
    def test_studio_creation(self):
        # Test apakah studio dibuat dengan benar
        self.assertEqual(self.studio.nama_studio, "Test Yoga Studio")
        self.assertEqual(self.studio.kota, "Jakarta")
        self.assertEqual(self.studio.area, "Menteng")
        self.assertEqual(self.studio.alamat, "Jl. Test No. 123")
        self.assertEqual(self.studio.nomor_telepon, "081234567890")
        self.assertIsInstance(self.studio.id, uuid.UUID)
    
    def test_studio_str_method(self):
        # Test method __str__ mengembalikan nama studio
        self.assertEqual(str(self.studio), "Test Yoga Studio")
    
    def test_studio_kota_choices(self):
        # Test bahwa field kota memiliki pilihan yang benar
        kota_values = [choice[0] for choice in KOTA_CHOICES]
        self.assertIn('Jakarta', kota_values)
        self.assertIn('Bogor', kota_values)
        self.assertIn('Depok', kota_values)
        self.assertIn('Tangerang', kota_values)
        self.assertIn('Bekasi', kota_values)
    
    def test_studio_optional_fields(self):
        # Test bahwa field opsional dapat dikosongkan atau bernilai null
        studio_minimal = Studio.objects.create(
            nama_studio="Minimal Studio",
            kota="Depok",
            area="UI",
            alamat="Jl. Minimal",
            nomor_telepon="081111111111"
        )
        self.assertIsNone(studio_minimal.thumbnail)
        self.assertIsNone(studio_minimal.gmaps_link)
    
    def test_studio_get_kota_display(self):
        # Test method get_kota_display
        self.assertEqual(self.studio.get_kota_display(), "Jakarta")

class StudioFormTest(TestCase):
    # Test cases untuk StudioForm
    
    def test_valid_form(self):
        # Test form dengan data yang valid
        form_data = {
            'nama_studio': 'New Yoga Studio',
            'thumbnail': 'https://example.com/image.jpg',
            'kota': 'Bogor',
            'area': 'Bogor Tengah',
            'alamat': 'Jl. Bogor No. 1',
            'gmaps_link': 'https://maps.google.com/bogor',
            'nomor_telepon': '082222222222'
        }
        form = StudioForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_missing_required_fields(self):
        # Test form dengan data tidak valid (missing required fields)
        form_data = {
            'nama_studio': 'Incomplete Studio',
        }
        form = StudioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('kota', form.errors)
        self.assertIn('area', form.errors)
        self.assertIn('alamat', form.errors)
        self.assertIn('nomor_telepon', form.errors)
    
    def test_form_fields_exist(self):
        # Test bahwa form memiliki semua field yang diperlukan
        form = StudioForm()
        expected_fields = ['nama_studio', 'thumbnail', 'kota', 'area', 
                          'alamat', 'gmaps_link', 'nomor_telepon']
        for field in expected_fields:
            self.assertIn(field, form.fields)

class StudioViewTest(TestCase):
    # Test cases untuk Studio views

    def setUp(self):
        # Set up test client dan test data
        self.client = Client()
        
        # Buat user reguler
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            kota='Jakarta'
        )
        
        # Buat user admin
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )
        
        # Buat test studio
        self.studio_jakarta = Studio.objects.create(
            nama_studio="Jakarta Yoga Studio",
            kota="Jakarta",
            area="Sudirman",
            alamat="Jl. Sudirman No. 1",
            nomor_telepon="081111111111"
        )
        
        self.studio_bogor = Studio.objects.create(
            nama_studio="Bogor Pilates Studio",
            kota="Bogor",
            area="Bogor Kota",
            alamat="Jl. Bogor No. 2",
            nomor_telepon="082222222222"
        )
    
    def test_show_studio_view(self):
        # Test fungsi show_studio mengembalikan template yang benar
        response = self.client.get(reverse('studio:show_studio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studio/studio.html')
    
    def test_show_json_view_authenticated_user(self):
        # Test fungsi show_json untuk user yang sudah login dengan preferensi kota
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('studio:show_json'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertEqual(data['user_kota'], 'Jakarta')
        self.assertIsInstance(data['cities'], list)
        
        # Cek apakah kota user muncul pertama
        self.assertEqual(data['cities'][0]['name'], 'Jakarta')
        self.assertTrue(data['cities'][0]['is_user_city'])
    
    def test_show_json_view_unauthenticated_user(self):
        # Test show_json view untuk user yang tidak terautentikasi
        response = self.client.get(reverse('studio:show_json'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsNone(data['user_kota'])
        self.assertIsInstance(data['cities'], list)
    
    def test_show_json_view_user_without_profile(self):
        # Test fungsi show_json untuk user tanpa profil
        user_no_profile = User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        response = self.client.get(reverse('studio:show_json'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsNone(data['user_kota'])
    
    def test_show_json_view_returns_correct_studios(self):
        # Test bahwa show_json mengembalikan studio yang dikelompokkan berdasarkan kota
        response = self.client.get(reverse('studio:show_json'))
        data = json.loads(response.content)

        # Temukan kota Jakarta dalam respons
        jakarta_city = next((city for city in data['cities'] if city['name'] == 'Jakarta'), None)
        self.assertIsNotNone(jakarta_city)
        self.assertEqual(len(jakarta_city['studios']), 1)
        self.assertEqual(jakarta_city['studios'][0]['nama_studio'], 'Jakarta Yoga Studio')
    
    def test_add_studio_view_requires_login(self):
        # Test bahwa add_studio memerlukan login
        response = self.client.get(reverse('studio:add_studio'))
        self.assertEqual(response.status_code, 302)  # Redirect ke login
        self.assertIn('/users/login/', response.url)
    
    def test_add_studio_view_requires_admin(self):
        # Test bahwa add_studio memerlukan user admin
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('studio:add_studio'))
        self.assertEqual(response.status_code, 302)  # Redirect ke login
    
    def test_add_studio_view_admin_get(self):
        # Test fungsi add_studio GET untuk user admin
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('studio:add_studio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studio/add_studio.html')
        self.assertIn('form', response.context)
    
    def test_add_studio_view_admin_post_valid(self):
        # Test fungsi add_studio POST dengan data valid
        self.client.login(username='admin', password='adminpass123')
        
        studio_data = {
            'nama_studio': 'New Test Studio',
            'kota': 'Tangerang',
            'area': 'BSD',
            'alamat': 'Jl. BSD No. 10',
            'nomor_telepon': '083333333333'
        }
        
        response = self.client.post(reverse('studio:add_studio'), data=studio_data)
        self.assertEqual(response.status_code, 302)  # Redirect setelah sukses
        self.assertRedirects(response, reverse('studio:show_studio'))
        
        # Cek apakah studio dibuat
        self.assertTrue(Studio.objects.filter(nama_studio='New Test Studio').exists())
    
    def test_add_studio_view_admin_post_invalid(self):
        # Test fungsi add_studio POST dengan data tidak valid
        self.client.login(username='admin', password='adminpass123')
        
        studio_data = {
            'nama_studio': 'Incomplete Studio',
            # Missing required fields
        }
        
        response = self.client.post(reverse('studio:add_studio'), data=studio_data)
        self.assertEqual(response.status_code, 200)  # Tetap di halaman form
        self.assertTemplateUsed(response, 'studio/add_studio.html')
    
    def test_delete_studio_view_requires_login(self):
        # Test bahwa delete_studio memerlukan login
        response = self.client.delete(
            reverse('studio:delete_studio', kwargs={'id': self.studio_jakarta.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect ke login

    def test_delete_studio_view_requires_admin(self):
        # Test bahwa delete_studio memerlukan user admin
        self.client.login(username='testuser', password='testpass123')
        response = self.client.delete(
            reverse('studio:delete_studio', kwargs={'id': self.studio_jakarta.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect ke login
    
    def test_delete_studio_view_admin_success(self):
        # Test delete_studio berhasil dihapus oleh admin
        self.client.login(username='admin', password='adminpass123')
        studio_id = self.studio_jakarta.id
        studio_name = self.studio_jakarta.nama_studio
        
        response = self.client.delete(
            reverse('studio:delete_studio', kwargs={'id': studio_id})
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn(studio_name, data['message'])
        
        # Verifikasi studio dihapus
        self.assertFalse(Studio.objects.filter(id=studio_id).exists())
    
    def test_delete_studio_view_nonexistent_studio(self):
        # Test delete_studio dengan ID studio yang tidak ada
        self.client.login(username='admin', password='adminpass123')
        fake_id = uuid.uuid4()
        
        response = self.client.delete(
            reverse('studio:delete_studio', kwargs={'id': fake_id})
        )
        self.assertEqual(response.status_code, 404)

class StudioURLTest(TestCase):
    # Test case untuk Studio URL
    
    def test_show_studio_url_resolves(self):
        # Test bahwa show_studio URL dituju dengan benar
        url = reverse('studio:show_studio')
        self.assertEqual(url, '/studio/')
    
    def test_add_studio_url_resolves(self):
        # Test bahwa add_studio URL dituju dengan benar
        url = reverse('studio:add_studio')
        self.assertEqual(url, '/studio/add/')
    
    def test_show_json_url_resolves(self):
        # Test bahwa show_json URL dituju dengan benar
        url = reverse('studio:show_json')
        self.assertEqual(url, '/studio/json/')
    
    def test_delete_studio_url_resolves(self):
        # Test bahwa delete_studio URL dituju dengan benar
        test_id = uuid.uuid4()
        url = reverse('studio:delete_studio', kwargs={'id': test_id})
        self.assertEqual(url, f'/studio/delete/{test_id}/')
