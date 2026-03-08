from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        response = self.client.post('/api/auth/register/', {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'Test@1234',
            'password2': 'Test@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_password_mismatch(self):
        response = self.client.post('/api/auth/register/', {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'Test@1234',
            'password2': 'Wrong@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        User.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='Test@1234'
        )
        response = self.client.post('/api/auth/login/', {
            'email': 'test@test.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='Test@1234'
        )
        response = self.client.post('/api/auth/login/', {
            'email': 'test@test.com',
            'password': 'Wrong@1234'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)