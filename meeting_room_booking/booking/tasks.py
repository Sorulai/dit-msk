from meeting_room_booking.celery import app
from .services import generate_report


@app.task
def generate_report_task(start_date, end_date, room_id=None):
    return generate_report(start_date, end_date, room_id)
