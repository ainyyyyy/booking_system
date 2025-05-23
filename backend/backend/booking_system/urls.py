"""
URL configuration for booking_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from easybook import views
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

router = routers.DefaultRouter()
# Register ViewSets
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'resources', views.ResourceViewSet, basename='resource')
router.register(r'bookings', views.BookingViewSet, basename='booking')



urlpatterns = [
    path('admin/', admin.site.urls),
    #path("", views.index, name="index"),
    #path('bookings/<int:bookingID>/', views.bookings, name="bookings"),
    path('users/<int:userID>/profile/', views.profile, name="profile"),
    path('users/<int:userID>/bookings/', views.user_bookings, name="user_bookings"),
    path('resources/<int:resourceID>/info/', views.resource_info, name="resource_info"),
    path('resources/<int:resourceID>/calendar/', views.calendar, name="calendar"),
    path('send/', views.run_task, name="run_task"),
    path('', include(router.urls)),

]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



