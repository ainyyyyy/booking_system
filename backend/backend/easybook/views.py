# from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from easybook.tasks import send_email_task
from rest_framework import viewsets
from easybook.models import Booking, User, Resource 
from easybook.serializers import BookingSerializer, UserSerializer, ResourceSerializer 

def index(request):
    return HttpResponse("Hi!")

def profile(request, userID):
    return HttpResponse("Your profile ID: %s" % userID)

def user_bookings(request, userID):
    return HttpResponse("Your profile ID: %s" % userID)

def bookings(request, bookingID):
    return HttpResponse(" %s." % bookingID)

def resource_info(request, resourceID):
    return HttpResponse(" %s." % resourceID)

def calendar(request, resourceID):
    return HttpResponse(" %s." % resourceID)

@csrf_exempt
def send_email_confirmation(request):
    task = send_email_task.delay(
        "Subject",
        "Message",
        "konishchevslava03@gmail.com"
    )
    return JsonResponse({"task_id": task.id}, status=202)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'userID'

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    lookup_field = 'resourseID' 

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    lookup_field = 'bookingID' 
