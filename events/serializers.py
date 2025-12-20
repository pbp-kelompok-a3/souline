from rest_framework import serializers
from .models import Event
from studio.models import Studio

class EventSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.nama_studio', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'date', 'poster', 'location', 'location_name', 'owner']
