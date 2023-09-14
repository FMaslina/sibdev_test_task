from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
User = get_user_model()


class CurrencyModel(models.Model):
    currency_name = models.CharField(max_length=3, verbose_name='Название валюты')


class QuoteModel(models.Model):
    currency = models.ForeignKey(CurrencyModel, on_delete=models.CASCADE, verbose_name='Валюта')
    quote = models.FloatField(verbose_name='Котировка')
    date = models.DateField(verbose_name="Дата")


class CurrencyUserModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    currency = models.ForeignKey(CurrencyModel, on_delete=models.CASCADE, verbose_name='Валюта')
    limit_value = models.FloatField(verbose_name="Пороговое значение")
