from django.urls import path
from quotes.views import GetArchiveQuotes, AddCurrencyToTracked, GetLastQuotes

urlpatterns = [
    path('quotes/archive', GetArchiveQuotes.as_view(), name='get_archive_quotes'),
    path('currency/user_currency', AddCurrencyToTracked.as_view(), name='add_currency_to_tracked'),
    path('rates', GetLastQuotes.as_view(), name='rates'),
]
