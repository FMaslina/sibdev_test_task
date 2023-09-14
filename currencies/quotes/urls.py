from django.urls import path
from quotes.views import GetArchiveQuotes

urlpatterns = [
    path('quotes/archive', GetArchiveQuotes.as_view(), name='get_archive_quotes'),
]