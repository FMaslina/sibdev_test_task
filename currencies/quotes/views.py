from datetime import datetime, timedelta
import requests
from django.db.models import Max, Min
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quotes.models import CurrencyModel, QuoteModel, CurrencyUserModel
from quotes.serializers import QuoteModelSerializer


# Create your views here.


class GetArchiveQuotes(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_start = datetime.now() - timedelta(days=30)

        while date_start <= datetime.today():
            formatted_month = str(date_start.month).zfill(2)
            formatted_day = str(date_start.day).zfill(2)

            data = requests.request('GET', "https://www.cbr-xml-daily.ru/archive/{0}/{1}/{2}/daily_json.js".format(
                date_start.year, formatted_month, formatted_day
            )).json()

            try:
                valutes = data['Valute']
                for currency in valutes.values():
                    currency_obj = CurrencyModel.objects.filter(currency_name=currency['CharCode'])
                    if not currency_obj.exists():
                        currency_obj = CurrencyModel.objects.create(currency_name=currency['CharCode'])
                    else:
                        currency_obj = currency_obj.first()

                    if QuoteModel.objects.filter(date=date_start).exists():
                        pass
                    else:
                        QuoteModel.objects.create(currency=currency_obj, quote=currency['Value'], date=date_start)

                date_start += timedelta(days=1)
            except KeyError:
                date_start += timedelta(days=1)

        return Response(status=status.HTTP_201_CREATED)


class AddCurrencyToTracked(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        currency_id = request.data['currency_id']
        limit = request.data['limit_value']

        currency_obj = CurrencyModel.objects.filter(id=currency_id)
        if currency_obj.exists():
            if not CurrencyUserModel.objects.filter(user=user, currency=currency_obj.first()).exists():
                CurrencyUserModel.objects.create(user=user, currency=currency_obj.first(), limit_value=limit)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetLastQuotes(APIView):
    def get(self, request):
        user = request.user
        ordering = self.request.query_params.get('ordering')
        last_quotes_date = QuoteModel.objects.all().last().date
        if ordering == 'asc':
            last_quotes = QuoteModel.objects.filter(date=last_quotes_date).order_by('quote')
        elif ordering == 'desc':
            last_quotes = QuoteModel.objects.filter(date=last_quotes_date).order_by('-quote')
        else:
            last_quotes = QuoteModel.objects.filter(date=last_quotes_date)
        result = []
        if user.is_authenticated:
            user_tracked_currencies = CurrencyUserModel.objects.filter(user=user)

            for currency in user_tracked_currencies:
                quote = last_quotes.filter(currency=currency.currency).first()
                result.append(QuoteModelSerializer(quote).data)
        else:
            result = QuoteModelSerializer(last_quotes, many=True).data

        return Response(status=status.HTTP_200_OK, data=result)


class AnalyticsCurrency(APIView):
    def get(self, request, pk):
        limit_value = int(request.query_params.get('threshold'))
        date_from = request.query_params.get('date_from')
        date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
        date_to = request.query_params.get('date_to')
        date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
        data = []

        currency = CurrencyModel.objects.get(pk=pk)
        currency_quotes = QuoteModel.objects.filter(date__in=[date_from_dt, date_to_dt], currency=currency)

        for quote in currency_quotes:
            if quote.quote > limit_value:
                exceeding_threshold = 'Превышено пороговое значение'
            elif quote.quote == limit_value:
                exceeding_threshold = 'Котировка равна пороговому значению'
            else:
                exceeding_threshold = 'Котировека меньше порогового значения'

            is_max = False
            is_min = False

            if quote.quote == currency_quotes.aggregate(Max('quote')):
                is_max = True
            if quote.quote == currency_quotes.aggregate(Min('quote')):
                is_min = True

            percentage = quote.quote / limit_value * 100

            data.append({
                "currency": currency.currency_name,
                "quote": quote.quote,
                "date": quote.date,
                "exceeding_threshold": exceeding_threshold,
                "is_max": is_max,
                "is_min": is_min,
                "percentage": percentage
            })

        return Response(status=status.HTTP_200_OK, data=data)
