from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


User = get_user_model()


class CreateUserViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_create_user_success(self):
        data = {'username': 'testuser', 'password': 'testpassword', 'email': 'test@test.com'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_create_user_failure(self):
        data = {'username': '', 'password': 'testpassword'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

        self.assertIn('username', response.data)


class JWTTokenCreationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@test.com')
        self.url = reverse('login_jwt')

    def test_create_jwt_token_success(self):
        data = {
            'email': 'test@test.com',
            'password': 'testpassword'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_create_jwt_token_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'invalidpassword'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_jwt_token_missing_credentials(self):
        data = {}

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
