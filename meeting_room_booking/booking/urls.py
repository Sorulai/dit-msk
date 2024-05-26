from django.urls import path
from .views import MeetingRoomList, BookingCreate, BookingCancel, RoomBookingView, RegisterUserAPIView, \
    MultipleBookingCreateAPIView, GenerateReportView, DownloadReportView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserLoginSerializer

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(serializer_class=UserLoginSerializer), name='login'),
    path('rooms/', MeetingRoomList.as_view(), name='meetingroom-list'),
    path('bookings/<int:pk>/', RoomBookingView.as_view({'get': 'list'}), name='booking-list'),
    path('bookings/create/', BookingCreate.as_view(), name='booking-create'),
    path('bookings/create/multiple/', MultipleBookingCreateAPIView.as_view(), name='multiple-booking-create'),
    path('bookings/cancel/<int:pk>/', BookingCancel.as_view(), name='booking-cancel'),
    path('report/', GenerateReportView.as_view(), name='generate-report'),
    path('report/download/<str:task_id>/', DownloadReportView.as_view(), name='download-report'),
]
