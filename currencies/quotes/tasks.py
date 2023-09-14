from datetime import datetime
import requests
from celery import shared_task
from quotes.models import CurrencyModel, QuoteModel


@shared_task
def get_quotes():
    data = requests.request("GET", "https://www.cbr-xml-daily.ru/daily_json.js").json()
    valutes = data['Valute']
    for currency in valutes.values():
        currency_obj = CurrencyModel.objects.filter(currency_name=currency['CharCode'])
        if not currency_obj.exists():
            currency_obj = CurrencyModel.objects.create(currency_name=currency['CharCode'])
        else:
            currency_obj = currency_obj.first()
        QuoteModel.objects.create(currency=currency_obj, quote=currency['Value'], date=datetime.now)
    return data
