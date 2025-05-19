from rest_framework import serializers
from .models import FlightSchedule, FlightReservation

class FlightScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightSchedule
        fields = '__all__'

class FlightReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightReservation
        fields = '__all__'