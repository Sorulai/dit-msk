import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import MeetingRoom, Booking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(TokenObtainPairSerializer):
    pass


class MeetingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRoom
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['room', 'start_time', 'end_time', 'purpose']
        extra_kwargs = {
            'start_time': {'required': True},
            'end_time': {'required': True}
        }

    def validate(self, attrs):
        start_time = attrs['start_time']
        end_time = attrs['end_time']

        # Округляем время начала до начала текущего часа
        start_time = start_time.replace(minute=0, second=0, microsecond=0)

        # Округляем время окончания до конца текущего часа, если оно ровно на час
        if end_time.minute == 0:
            end_time = (end_time - datetime.timedelta(minutes=1)).replace(second=59)
        else:
            end_time = end_time.replace(minute=59, second=59)

        if end_time <= start_time:
            raise serializers.ValidationError("End time must be greater than start time")

        # Проверяем, есть ли уже запись на это время
        existing_booking = Booking.objects.filter(
            start_time__lte=end_time,
            end_time__gte=start_time,
            room=attrs['room']
        ).exists()

        if existing_booking:
            raise serializers.ValidationError("Booking already exists for this time")

        if start_time.time() < datetime.time(7, 0) or end_time.time() > datetime.time(23, 0):
            raise serializers.ValidationError("Booking must be between 7:00 and 23:00")

        attrs['start_time'] = start_time
        attrs['end_time'] = end_time
        return attrs

    def create(self, validated_data):
        # Пользователь берется из запроса
        user = self.context['request'].user
        booking = Booking.objects.create(user=user, **validated_data)
        return booking


class MultipleBookingSerializer(serializers.Serializer):
    bookings = BookingSerializer(many=True)

    def create(self, validated_data):
        bookings_data = validated_data['bookings']
        user = self.context['request'].user
        bookings = []

        for booking_data in bookings_data:
            booking = Booking.objects.create(user=user, **booking_data)
            bookings.append(booking)

        return bookings


class MeetingRoomBookingSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = MeetingRoom
        fields = ['id', 'name', 'time']


class RoomBookingSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    end_time = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    flag = serializers.BooleanField()


class BookingDetailSerializer(serializers.ModelSerializer):
    is_free = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['room', 'start_time', 'end_time', 'purpose', 'is_free']

    def get_is_free(self, obj):
        now = timezone.now()
        return obj.start_time > now or obj.end_time < now


class GenerateReportSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    end_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    room_id = serializers.IntegerField(required=False)
