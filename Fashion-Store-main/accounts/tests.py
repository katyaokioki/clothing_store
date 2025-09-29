from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import UserAddress

User = get_user_model()

class AccountViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.add_address_url = reverse('add_address')
        self.address_list_url = reverse('address_list')
        self.profile_url = reverse('profile')
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass123')

    def test_signup_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_signup_post_creates_user(self):
        response = self.client.post(self.signup_url, {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'name': 'New User',
            'phone': '1234567890'
        })
        self.assertRedirects(response, '/accounts/login/')
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_signup_post_existing_email(self):
        response = self.client.post(self.signup_url, {
            'email': self.user.email,
            'password': 'pass',
        }, follow=True)
        self.assertRedirects(response, self.signup_url)
        messages = list(response.context['messages'])
        self.assertTrue(any("Email already in use" in str(m) for m in messages))

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_post_valid(self):
        response = self.client.post(self.login_url, {
            'email': self.user.email,
            'password': 'testpass123',
        })
        self.assertRedirects(response, '/')

    def test_login_post_invalid(self):
        response = self.client.post(self.login_url, {
            'email': self.user.email,
            'password': 'wrongpass',
        }, follow=True)
        self.assertRedirects(response, self.login_url)
        messages = list(response.context['messages'])
        self.assertTrue(any("Invalid credentials" in str(m) for m in messages))

    def test_logout(self):
        self.client.login(email=self.user.email, password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, '/')

    def test_add_address_post(self):
        self.client.login(email=self.user.email, password='testpass123')
        response = self.client.post(self.add_address_url, {
            'address_line': '123 Street',
            'city': 'City',
            'state': 'State',
            'postal_code': '12345',
            'country': 'Country',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserAddress.objects.filter(user=self.user, address_line='123 Street').exists())

    def test_add_address_post_missing_address(self):
        self.client.login(email=self.user.email, password='testpass123')
        response = self.client.post(self.add_address_url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Please add address" in str(m) for m in messages))

    def test_profile_view_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        self.client.login(email=self.user.email, password='testpass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)

    def test_address_list_view_shows_addresses(self):
        self.client.login(email=self.user.email, password='testpass123')
        UserAddress.objects.create(user=self.user, address_line="My Address")
        response = self.client.get(self.address_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Address")

    def test_edit_address_get_and_post(self):
        self.client.login(email=self.user.email, password='testpass123')
        address = UserAddress.objects.create(user=self.user, address_line="Old Address")

        edit_url = reverse('edit_address', args=[address.id])
        # GET request renders form
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Old Address")

        # POST updates address and redirects
        response = self.client.post(edit_url, {
            'address_line': 'New Address',
            'city': 'New City',
            'state': 'New State',
            'postal_code': '54321',
            'country': 'New Country',
        })
        self.assertRedirects(response, self.address_list_url)
        address.refresh_from_db()
        self.assertEqual(address.address_line, 'New Address')
        self.assertEqual(address.city, 'New City')
