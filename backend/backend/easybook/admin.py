from django.contrib import admin

from .models import User
from .models import Resource
from .models import Booking

admin.site.register(User)
admin.site.register(Resource)
admin.site.register(Booking)
