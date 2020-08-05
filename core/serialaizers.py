from rest_framework import serializers

from core.models import WorkPlace, Reservation


class WorkPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPlace
        fields = ('id', 'name', 'address')


class ReservationSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ('date_from', 'date_to', 'username')

    def get_username(self, reservation):
        return reservation.user.username
