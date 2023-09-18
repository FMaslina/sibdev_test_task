from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from quotes.models import CurrencyModel, CurrencyUserModel, QuoteModel

User = get_user_model()


class AddCurrencyToTrackedTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('add_currency_to_tracked')
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@test.com')
        self.client.force_authenticate(user=self.user)
        self.currency = CurrencyModel.objects.create(currency_name='USD')

    def test_add_currency_to_tracked_success(self):
        data = {
            'currency_id': self.currency.id,
            'limit_value': 100.0
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CurrencyUserModel.objects.filter(user=self.user, currency=self.currency).exists())

    def test_add_existing_currency_to_tracked(self):
        CurrencyUserModel.objects.create(user=self.user, currency=self.currency, limit_value=100.0)

        data = {
            'currency_id': self.currency.id,
            'limit_value': 200.0
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_nonexistent_currency_to_tracked(self):
        data = {
            'currency_id': 999,
            'limit_value': 200.0
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetLastQuotesTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('rates')
        self.currency = CurrencyModel.objects.create(currency_name='USD')
        self.quote = QuoteModel.objects.create(currency=self.currency, quote=75.0, date=datetime.now())

    def test_get_last_quotes_uncached(self):
        cache.clear()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.quote.quote, response.data[0]['quote'])

    def test_get_last_quotes_cached(self):
        cache.set(self.url, [{"quote": 75.0}], 60*15)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.quote.quote, response.data[0]['quote'])

    def test_get_last_quotes_empty_cache(self):
        cache.clear()

        with self.settings(CACHE_MIDDLEWARE_SECONDS=0):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.quote.quote, response.data[0]['quote'])


class AnalyticsCurrencyTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('currency_analytics', args=[1])
        self.currency = CurrencyModel.objects.create(currency_name='USD')
        self.quote1 = QuoteModel.objects.create(currency=self.currency, quote=75.0, date='2023-09-01')
        self.quote2 = QuoteModel.objects.create(currency=self.currency, quote=80.0, date='2023-09-02')
        self.quote3 = QuoteModel.objects.create(currency=self.currency, quote=70.0, date='2023-09-03')

    def test_analytics_currency_valid_data(self):
        data = {
            'threshold': 74.0,
            'date_from': '2023-09-01',
            'date_to': '2023-09-03',
        }

        response = self.client.get(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self.assertEqual(response.data[0]['exceeding_threshold'], 'Превышено пороговое значение')
        self.assertEqual(response.data[0]['is_max'], False)
        self.assertEqual(response.data[0]['is_min'], False)

    def test_analytics_currency_invalid_data(self):
        data = {
            'threshold': 'invalid_threshold',
            'date_from': 'invalid_date',
            'date_to': 'invalid_date',
        }

        response = self.client.get(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)