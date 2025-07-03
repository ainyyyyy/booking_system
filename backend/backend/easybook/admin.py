from django.contrib import admin
from .models import Resource
from .models import Booking
from django.contrib.auth.admin import UserAdmin
from .models import User, AvailabilityRule, CapacityWindow
from .forms import CustomUserChangeForm, CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "organization_name",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "organization_name",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": (
            "first_name",
            "last_name", 
            "email", 
            "password", 
            "phone_number",
            "date_of_birth",
            "organization_name",
            "organization_description",)}
        ),
        ("Permissions", {"fields": (
            "is_staff", 
            "is_active", 
            "groups", 
            "user_permissions")}
        ),
    )
    add_fieldsets = (
        ( None, {"fields": (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "phone_number",
            "date_of_birth",
            "organization_name",
            "organization_description",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions")}
        ),
    )
    search_fields = ("email", "first_name", "last_name", "phone_number", "organization_name")
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Resource)
admin.site.register(AvailabilityRule)
admin.site.register(CapacityWindow)
admin.site.register(Booking)
