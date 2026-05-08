from rest_framework import serializers
from .models import ELDLog

class EldLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELDLog
        fields = "__all__"
