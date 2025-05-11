from datetime import datetime, time

from easybook.models import Booking, Resource, User

def test_user(user: User):
    assert user.userID == 0
    assert user.email == "konishchevslava03@gmail.com"
    assert user.name == "Vyacheslav"
    assert user.surname == "Konischev"

def test_resource(resource: Resource):
    assert resource.resourseID == 0
    assert resource.name == "Coworking"
    assert resource.description == "The best coworking in the world"
    schedule = {
        "Mon": ["8:00", "18:00"], 
        "Tue": ["10:00", "20:00"], 
        "Wed": ["9:00", "19:30"], 
        "Thu": ["9:00", "18:00"], 
    }
    assert resource.schedule == schedule

def test_booking(booking: Booking, user: User, resource: Resource):
    assert booking.bookingID == 0
    assert booking.user == user
    assert booking.resource == resource
    assert booking.start_time == datetime(2025, 12, 28, 17, 55)
    assert booking.end_time == datetime(2025, 12, 28, 23, 55)
    assert booking.is_confirmed == True