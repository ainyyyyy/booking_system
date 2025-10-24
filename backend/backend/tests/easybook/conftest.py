import pytest
#from django.urls import reverse
#from datetime import datetime, date, time
from easybook.models import Booking, User, Resource, Company, Staff, ResourceStaff


@pytest.fixture
def user(db):
    return User.objects.create(
        email="am@g.com",
        password="123",
        first_name="Vyacheslav",
        last_name="Konischev"
    )

@pytest.fixture
def company(db):
    return Company.objects.create(
        name = "Company_name",
        slug = "company_name"
    )

@pytest.fixture
def other_company(db):
    return Company.objects.create(
        name = "Other_company_name",
        slug = "other_company_name"
    )

@pytest.fixture
def resource(db, user, company):
    return Resource.objects.create(
        user = user,
        company=company,
        name = "Coworking",
        description = "The best coworking in the world",
        max_capacity = 10
    )

@pytest.fixture
def other_resource(db, user, company):
    return Resource.objects.create(
        user=user, 
        company=company,
        name='Another Coworking', 
        max_capacity=20
    )

@pytest.fixture
def staff(db, user, company):
    return Staff.objects.create(
        user=user,
        company=company,
        display_name = "John Doe"
    )

@pytest.fixture
def other_company_staff(db, user, other_company):
    return Staff.objects.create(
        user=user,
        company=other_company,
        display_name = "Jane Doe"
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