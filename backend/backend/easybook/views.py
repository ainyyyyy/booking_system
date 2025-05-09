#from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from easybook.tasks import send_email_task

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
def run_task(request):
    #if request.POST:
        #task_type = request.POST.get("type")
    task = send_email_task.delay(
        "Subject", 
        "Message", 
        "konishchevslava03@gmail.com"
        )
    return JsonResponse({"task_id": task.id}, status=202)
