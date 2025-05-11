import pytest
#from django.urls import reverse
from datetime import datetime
from easybook.models import Booking, User, Resource


@pytest.fixture
def user(db):
    return User.objects.create(
        userID = 0,
        email = "konishchevslava03@gmail.com",
        name = "Vyacheslav",
        surname = "Konischev",
    )

@pytest.fixture
def resource(db):
    return Resource.objects.create(
        resourseID = 0,
        name = "Coworking",
        description = "The best coworking in the world",
        schedule = {            
            "Mon": ["8:00", "18:00"], 
            "Tue": ["10:00", "20:00"], 
            "Wed": ["9:00", "19:30"], 
            "Thu": ["9:00", "18:00"], 
        },
    )

@pytest.fixture
def booking(db, user, resource):
    return Booking.objects.create(
        bookingID = 0,
        user = user,
        resource = resource,
        start_time = datetime(2025, 12, 28, 17, 55),
        end_time = datetime(2025, 12, 28, 23, 55),
        is_confirmed = True,
    )
