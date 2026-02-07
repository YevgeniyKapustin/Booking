from datetime import datetime

from src.core.email import send_email
from src.tasks.celery_app import celery_app


@celery_app.task(name="send_welcome_email")
def send_welcome_email(email: str, full_name: str) -> None:
    subject = "Welcome to Table Reservations"
    body = f"Hi {full_name}, your account is ready."
    send_email(email, subject, body)


@celery_app.task(name="send_booking_reminder")
def send_booking_reminder(email: str, full_name: str, start_time: str) -> None:
    subject = "Booking reminder"
    body = f"Hi {full_name}, reminder about your booking at {start_time}."
    send_email(email, subject, body)
