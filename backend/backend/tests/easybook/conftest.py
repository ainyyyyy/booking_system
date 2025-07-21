import pytest
#from django.urls import reverse
#from datetime import datetime, date, time
from easybook.models import Booking, User, Resource


@pytest.fixture
def user(db):
    return User.objects.create(
        email="am@g.com",
        password="123",
        first_name="Vyacheslav",
        last_name="Konischev"
    )

@pytest.fixture
def resource(db, user):
    return Resource.objects.create(
        user = user,
        name = "Coworking",
        description = "The best coworking in the world",
        max_capacity = 10
    )

"""@pytest.fixture
def daily_schedule(db, resource):
    return DailySchedule.objects.create(
        day = date(2025, 12, 28),
        start_time = time(8, 00),
        end_time = time(20, 30),
        resource = resource,
        max_capacity = 1,
    )

@pytest.fixture
def booking(db, user, resource):
    return Booking.objects.create(
        booking_id = 0,
        user = user,
        resource = resource,
        start_time = datetime(2025, 12, 28, 17, 55),
        end_time = datetime(2025, 12, 28, 23, 55),
        is_confirmed = True,
    )
"""
"""@pytest.fixture
def api_client():
   from rest_framework.test import APIClient
   return APIClient()"""