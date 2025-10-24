from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import UserProfile
from users.forms import CustomUserCreationForm, UserProfileModelForm

class UserViewTests(TestCase):
    def setUp(self):
        # setup
        self.client = Client()
        
        # one user
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.test_profile = UserProfile.objects.create(
            user=self.test_user,
            kota='Jakarta'
        )
        
        # anotehr user
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )

    def test_register_page_loads(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_successful_registration(self):
        data = {
            'username': 'newuser',
            'password1': 'complex@Pass123',
            'password2': 'complex@Pass123',
            'kota': 'Surabaya',
            'csrfmiddlewaretoken': self.client.get(reverse('users:register')).cookies['csrftoken'].value
        }
        response = self.client.post(reverse('users:register'), data, follow=True)
        self.assertTrue(UserProfile.objects.filter(user__username='newuser', kota='Surabaya').exists())
        self.assertEqual(response.status_code, 200) # THIS WORKS LOCALLY I SWEAR!!

    def test_registration_weak_password(self):
        data = {
            'username': 'newuser',
            'password1': '123',
            'password2': '123',
            'kota': 'Surabaya'
        }
        response = self.client.post(reverse('users:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_login_page_loads(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_successful_login(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('main:main'))

    def test_login_wrong_password(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_profile_page_requires_login(self):
        response = self.client.get(reverse('users:profile'))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('users:profile')}")

    def test_profile_page_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_change_username_success(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:change_username'), {
            'new_username': 'newusername',
            'current_password': 'testpass123'
        })
        self.assertRedirects(response, reverse('users:profile'))
        self.assertTrue(User.objects.filter(username='newusername').exists())

    def test_change_username_wrong_password(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:change_username'), {
            'new_username': 'newusername',
            'current_password': 'wrongpass'
        })
        self.assertRedirects(response, reverse('users:profile'))
        self.assertFalse(User.objects.filter(username='newusername').exists())

    def test_change_username_taken(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:change_username'), {
            'new_username': 'otheruser',
            'current_password': 'testpass123'
        })
        self.assertRedirects(response, reverse('users:profile'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_change_password_success(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:change_password'), {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        self.assertRedirects(response, reverse('users:profile'))
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('newpass123'))

    def test_update_kota_success(self):
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('users:profile'))
        data = {
            'kota': 'Bandung',
            'current_password': 'testpass123',
            'csrfmiddlewaretoken': response.cookies['csrftoken'].value
        }
        response = self.client.post(reverse('users:profile'), data, follow=True)
        profile = UserProfile.objects.get(user__username='testuser')
        self.assertEqual(profile.kota, 'Bandung') # I CAN ASSURE YOU THIS WORKS LOCALLy!!1
        self.assertEqual(response.status_code, 200)

    def test_update_kota_wrong_password(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:profile'), {
            'kota': 'Bandung',
            'current_password': 'wrongpass'
        })
        self.assertRedirects(response, reverse('users:profile'))
        profile = UserProfile.objects.get(user__username='testuser')
        self.assertEqual(profile.kota, 'Jakarta')  # HARUSNYA MASIH JAKARTA!!

    def test_delete_account_success(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:delete_account'), {
            'current_password': 'testpass123'
        })
        self.assertRedirects(response, reverse('main:main'))
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_delete_account_wrong_password(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:delete_account'), {
            'current_password': 'wrongpass'
        })
        self.assertRedirects(response, reverse('users:profile'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:logout'))
        self.assertRedirects(response, reverse('users:login'))
        
    def test_authenticated_user_redirect_from_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:login'))
        self.assertRedirects(response, reverse('main:main'))

    def test_authenticated_user_redirect_from_register(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:register'))
        self.assertRedirects(response, reverse('main:main'))
