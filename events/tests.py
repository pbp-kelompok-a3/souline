from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from .models import Event


class EventViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        # untuk test login_required
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        # Buat beberapa event untuk test
        self.event_today = Event.objects.create(
            name="Today Event",
            date=date.today(),
            description="Event today"
        )
        self.event_soon = Event.objects.create(
            name="Soon Event",
            date=date.today() + timedelta(days=3),
            description="Event soon"
        )
        self.event_later = Event.objects.create(
            name="Later Event",
            date=date.today() + timedelta(days=10),
            description="Event later"
        )

    def test_show_events_view(self):
        """Pastikan halaman event list bisa diakses"""
        response = self.client.get(reverse('events:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Today Event")

    def test_add_event_view_get(self):
        """Pastikan halaman add_event dapat diakses via GET"""
        response = self.client.get(reverse('events:add_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/add_event.html')

    def test_add_event_post(self):
        """Pastikan event baru bisa ditambahkan via POST"""
        response = self.client.post(reverse('events:add_event'), {
            'name': 'New Event',
            'date': date.today(),
            'description': 'New event desc',
        })
        self.assertEqual(response.status_code, 302)  # redirect sukses
        self.assertTrue(Event.objects.filter(name="New Event").exists())

    def test_json_all(self):
        """Pastikan show_json mengembalikan semua event"""
        response = self.client.get(reverse('events:show_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 3)

    def test_json_filter_soon(self):
        """Pastikan filter soon mengembalikan event dalam 7 hari"""
        response = self.client.get(reverse('events:show_json_filtered', args=['soon']))
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(all(
            date.today() <= datetime.strptime(d["date"], "%d %B %Y").date() <= date.today() + timedelta(days=7)
            for d in data
        ))

    def test_json_filter_later(self):
        """Pastikan filter later mengembalikan event setelah 7 hari"""
        response = self.client.get(reverse('events:show_json_filtered', args=['later']))
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(all(
            datetime.strptime(d["date"], "%d %B %Y").date() > date.today() + timedelta(days=7)
            for d in data
        ))