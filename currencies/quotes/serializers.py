from rest_framework import serializers
from .models import QuoteModel


class QuoteModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteModel
        fields = '__all__'
