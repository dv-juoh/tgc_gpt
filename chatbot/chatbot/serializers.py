from rest_framework import serializers
from .models import Input

class InputSerializer(serializers.ModelSerializer):
    context = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Input
        fields = {'promt', 'context'}