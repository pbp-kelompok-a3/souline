from django.test import TestCase
from django.urls import reverse
from .models import SportswearBrand
from .forms import SportswearBrandForm # Jika Anda membuat forms.py

class SportswearModelTest(TestCase):
    def setUp(self):
        SportswearBrand.objects.create(
            brand_name="Test Brand",
            description="A description.",
            link="http://test.com", 
            thumbnail_url="http://test.com/logo.png" 
        )

    def test_brand_creation(self):
        brand = SportswearBrand.objects.get(brand_name="Test Brand")
        self.assertEqual(brand.description, "A description.")
        self.assertTrue(isinstance(brand, SportswearBrand))

    def test_brand_str_method(self):
        brand = SportswearBrand.objects.get(brand_name="Test Brand")
        self.assertEqual(str(brand), "Test Brand")

class SportswearViewTest(TestCase):
    def setUp(self):
        self.brand1 = SportswearBrand.objects.create(
            brand_name="Brand A", 
            description="Desc A",
            link="http://a.com",
        )
        self.url = reverse('sportswear:show_sportswear') 

    def test_sportswear_list_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
    def test_sportswear_list_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'sportswear/sportswear_list.html') 

    def test_sportswear_list_data_displayed(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.brand1.brand_name)
        self.assertContains(response, self.brand1.description)

from django.contrib.auth import get_user_model
User = get_user_model()

class SportswearAdminTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            email='admin@test.com', 
            password='password123'
        )
        self.brand_to_delete = SportswearBrand.objects.create(
            brand_name="Delete Me", 
            description="Temp",
            link="http://del.com",
        )
        self.delete_url = reverse('sportswear:delete_brand', args=[self.brand_to_delete.pk])

    def test_delete_brand_unauthorized(self):
        response = self.client.post(self.delete_url)
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(SportswearBrand.objects.filter(pk=self.brand_to_delete.pk).exists())

    def test_delete_brand_successful(self):
        self.client.login(username='admin', password='password123')
        
        response = self.client.post(self.delete_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest') 
        
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(SportswearBrand.objects.filter(pk=self.brand_to_delete.pk).exists())