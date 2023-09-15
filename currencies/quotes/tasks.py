from datetime import datetime, timedelta
import requests
from celery import shared_task
from django.core.mail import send_mail

from quotes.models import CurrencyModel, QuoteModel, CurrencyUserModel


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
        if QuoteModel.objects.filter(date=datetime.today()).exists():
            pass
        else:
            QuoteModel.objects.create(currency=currency_obj, quote=currency['Value'], date=datetime.today())
    return data


@shared_task
def check_limits():
    last_quotes_date = QuoteModel.objects.all().last().date
    last_quotes = QuoteModel.objects.filter(date=last_quotes_date)
    users_quotes_tracks = CurrencyUserModel.objects.all()

    for user_quote in users_quotes_tracks:
        daily_currency_quote = last_quotes.get(currency=user_quote.currency)
        if daily_currency_quote.quote > user_quote.limit_value:
            send_mail(f'Превышено пороговое значение по валюте {daily_currency_quote.currency.currency_name}',
                      f'Превышено пороговое значение по {daily_currency_quote.currency.currency_name}, котировка - '
                      f'{daily_currency_quote.quote}', 'FMaslina@yandex.ru', ['FMaslina@yandex.ru'])
