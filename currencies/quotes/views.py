from datetime import datetime, timedelta
import requests
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from quotes.models import CurrencyModel, QuoteModel


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