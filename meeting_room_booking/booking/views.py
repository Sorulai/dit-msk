import os
from django.conf import settings
from .services import processing_dates
from .tasks import generate_report_task
from celery.result import AsyncResult
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import generics, permissions, viewsets
from rest_framework.permissions import AllowAny
from .models import MeetingRoom, Booking
from .serializers import MeetingRoomSerializer, BookingSerializer, RoomBookingSerializer, UserSerializer, \
    MultipleBookingSerializer, GenerateReportSerializer
from rest_framework.response import Response


class RegisterUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class MeetingRoomList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = MeetingRoom.objects.all()
    serializer_class = MeetingRoomSerializer


class RoomBookingView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = RoomBookingSerializer

    def list(self, request, pk):
        room = MeetingRoom.objects.get(pk=pk)
        results = processing_dates(room=room)

        serializer = RoomBookingSerializer(results, many=True)
        data = {
            'id': pk,
            'name': room.name,
            'times': serializer.data
        }
        return Response(data)


class MultipleBookingCreateAPIView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = MultipleBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bookings = serializer.save()
        return Response({'bookings': [BookingSerializer(booking).data for booking in bookings]})


class BookingCreate(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingCancel(generics.DestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


class GenerateReportView(generics.CreateAPIView):
    serializer_class = GenerateReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        room_id = serializer.validated_data['room_id']

        task = generate_report_task.delay(start_date, end_date, room_id)
        return Response({'task_id': task.id}, status=202)


class DownloadReportView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, task_id, *args, **kwargs):
        task = AsyncResult(task_id)
        if task.state == 'SUCCESS':
            file_name = task.result
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(),
                                        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{file_path}"'
                return response
        return Response({'status': task.state}, status=202)
