from django.contrib import admin
from .models import MeetingRoom, Booking


@admin.register(MeetingRoom)
class LessonMaterialsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Booking)
class LessonMaterialsAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user', 'start_time', 'end_time', 'purpose')
