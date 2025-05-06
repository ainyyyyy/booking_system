from django.shortcuts import render
from django.http import HttpResponse

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