# Generated by Django 5.0.6 on 2024-05-25 11:04

from django.db import migrations


def add_meeting_rooms(apps, schema_editor):
    MeetingRoom = apps.get_model('booking', 'MeetingRoom')
    rooms = [
        "Room 1",
        "Room 2",
        "Room 3",
        "Room 4",
        "Room 5",
    ]
    for room_name in rooms:
        MeetingRoom.objects.create(name=room_name)


class Migration(migrations.Migration):
    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_meeting_rooms),
    ]
