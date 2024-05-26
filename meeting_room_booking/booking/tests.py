from datetime import datetime, timedelta
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.utils import timezone
from booking.models import MeetingRoom, Booking


class MeetingRoomBookingAPITestCase(APITestCase):

    def setUp(self):
        """
            Настройка
        """
        self.username = "testuser"
        self.password = "password123"
        self.email = "testuser@example.com"
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        self.client.force_authenticate(user=self.user)

        self.room = MeetingRoom.objects.create(name="Test Room")
        self.booking = Booking.objects.create(
            room=self.room,
            user=self.user,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            purpose="Test Booking"
        )

    def test_list_meeting_rooms(self):
        """
        Тест - список всех конференц-залов, доступных в офисе
        """
        response = self.client.get("/api/rooms/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.json()[0])

    def test_create_booking(self):
        """
        Тест - Успешное создание бронирования
        """
        response = self.client.get("/api/rooms/")
        room_id = response.json()[0]["id"]

        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        data = {
            "room": room_id,
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "purpose": "Team Meeting"
        }

        response = self.client.post("/api/bookings/create/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["purpose"], "Team Meeting")

    def test_booking_conflict(self):
        """
        Тест - создание бронирования с уже занятыми датами
        """
        response = self.client.get("/api/rooms/")
        room_id = response.json()[0]["id"]

        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        data = {
            "room": room_id,
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "purpose": "Initial Meeting"
        }
        response = self.client.post("/api/bookings/create/", data, format="json")
        self.assertEqual(response.status_code, 201)

        conflict_data = {
            "room": room_id,
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "purpose": "Conflict Meeting"
        }
        conflict_response = self.client.post("/api/bookings/create/", conflict_data, format="json")
        self.assertEqual(conflict_response.status_code, 400)

    def test_list_bookings(self):
        """
        Тест - список всех бронирований на день зала по часам,
        в том числе и уже забронированных
        """
        response = self.client.get("/api/rooms/")
        room_id = response.json()[0]["id"]

        response = self.client.get(f"/api/bookings/{room_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("start_time", response.json()["times"][0])

    def test_cancel_booking(self):
        """
        Тест - Отмена бронирования
        """
        response = self.client.get("/api/rooms/")
        room_id = response.json()[0]["id"]

        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        data = {
            "room": room_id,
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "purpose": "Team Meeting"
        }

        response = self.client.post("/api/bookings/create/", data, format="json")
        booking_id = response.json()["room"]

        response = self.client.delete(f"/api/bookings/cancel/{booking_id}/")
        self.assertEqual(response.status_code, 204)

    def test_generate_report(self):
        """
        Тест - генерация отчета
        """
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        data = {
            "start_date": start_date,
            "end_date": end_date,
        }
        response = self.client.post("/api/report/", data, format="json")
        self.assertEqual(response.status_code, 202)
        self.assertIn("task_id", response.json())

    def test_generate_report_invalid_dates(self):
        """
           Тест - генерация отчета с невалидными данными
        """
        data = {
            "start_date": "invalid-date",
            "end_date": "invalid-date",
        }
        response = self.client.post("/api/report/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("start_date", response.json())
        self.assertIn("end_date", response.json())

    def test_download_report(self):
        """
        Тест - загрузка отчета
        """
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        data = {
            "start_date": start_date,
            "end_date": end_date,
        }
        response = self.client.post("/api/report/", data, format="json")
        task_id = response.json()["task_id"]

        from time import sleep
        from celery.result import AsyncResult
        async_result = AsyncResult(task_id)
        while not async_result.ready():
            sleep(1)

        response = self.client.get(f"/api/report/download/{task_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'],
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.assertIn("attachment; filename=", response['Content-Disposition'])

    def test_download_report_invalid_task_id(self):
        """
        Тест - загрузка отчета с невалидным айди
        """
        invalid_task_id = "invalid-task-id"
        response = self.client.get(f"/api/report/download/{invalid_task_id}/")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()["status"], "PENDING")
