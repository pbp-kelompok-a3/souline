from django.test import TestCase, Client
from django.urls import reverse
from .models import Resource
import json

class ResourceViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # buat resource dummy
        self.resource = Resource.objects.create(
            title="Test Video",
            description="Test Description",
            youtube_url="https://youtu.be/dQw4w9WgXcQ",
            level="beginner"
        )

    # ============================
    # TEST TEMPLATE VIEWS
    # ============================
    def test_resource_list_page(self):
        response = self.client.get(reverse('resources:resource_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources/resources_list.html')

    def test_resource_form_page(self):
        response = self.client.get(reverse('resources:resource_form_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources/resources_form.html')

    def test_resource_edit_page(self):
        response = self.client.get(reverse('resources:resource_edit_page', args=[self.resource.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources/resources_edit.html')
        self.assertContains(response, str(self.resource.id))

    def test_resource_detail_page(self):
        response = self.client.get(reverse('resources:resource_detail_page', args=[self.resource.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources/resources_detail.html')
        self.assertContains(response, self.resource.title)

    # ============================
    # TEST API VIEWS
    # ============================
    def test_resource_list_api(self):
        response = self.client.get(reverse('resources:resource_list_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.resource.title)

    def test_add_resource(self):
        payload = {
            "title": "New Video",
            "description": "New Desc",
            "youtube_url": "https://youtu.be/test123",
            "level": "intermediate"
        }
        response = self.client.post(
            reverse('resources:add_resource'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(Resource.objects.filter(title="New Video").exists())

    def test_edit_resource(self):
        payload = {"title": "Updated Title"}
        response = self.client.post(
            reverse('resources:edit_resource', args=[self.resource.id]),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'updated')
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.title, "Updated Title")

    def test_delete_resource(self):
        response = self.client.post(reverse('resources:delete_resource', args=[self.resource.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'deleted')
        self.assertFalse(Resource.objects.filter(id=self.resource.id).exists())
