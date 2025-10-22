from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    AvailabilityRule,
    CapacityWindow,
    Company,
    Booking,
    Resource,
    Category
)
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.postgres.forms import RangeWidget, DateTimeRangeField
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminSplitDateTime


class CombinedDateTimeRangeField(DateTimeRangeField):
    def combine(self, value):
        if (
            value 
            and len(value)==2
            and len(value[0])==2
            and value[0][0]
            and value[0][1]
            and len(value[1])==2
            and value[1][0]
            and value[1][1]
        ):
            return [
                f"{value[0][0]}T{value[0][1]}", 
                f"{value[1][0]}T{value[1][1]}"
            ]
        return [None, None]

    def clean(self, value):
        value = self.combine(value)
        return super().clean(value)

    def has_changed(self, initial, data):
        data = self.combine(data)
        return super().has_changed(initial, data)


class BookingForm(ModelForm):
    timerange = CombinedDateTimeRangeField(widget=RangeWidget(AdminSplitDateTime))
    class Meta:
        model = Booking
        fields = "__all__"


# @admin.register(Company)
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = (
#         'name', 
#         'description', 
#         'logo', 
#         'is_active',
#     )
#     list_filter = ('name', 'is_active')


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = (
#         'company', 
#         'parent', 
#         'name',
#         'description',
#         'sort_order',
#         'is_active',
#     )
#     list_filter = (
#         'name', 
#         'company',
#         'parent',
#         'sort_order',
#         'is_active'
#     )


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_capacity')
    list_filter = ('max_capacity',)

    fieldsets = (
        (None, {
            'fields': (
                'view_bookings_link', 
                'view_availability_rules_link', 
                'view_capacity_windows_link'
            ),
        }),
        (None, {
            'fields': (
                'name', 
                'user', 
                'description',
                'max_capacity'
            )
        }),
    )
    readonly_fields = (
        'view_bookings_link', 
        'view_availability_rules_link', 
        'view_capacity_windows_link'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def view_bookings_link(self, obj):
        if not obj.pk:
            return "-"
        # Формируем url для списка бронирований, 
        # отфильтрованный по id текущего ресурса
        url = (
            reverse("admin:easybook_booking_changelist")
            + f"?resource__id__exact={obj.id}"
        )
        return format_html(
            '<a href="{}">Bookings ({})</a>', 
            url, 
            obj.booking_set.count()
        )
    #view_bookings_link.short_description = "Бронирования"

    def view_availability_rules_link(self, obj):
        if not obj.pk:
            return "-"
        url = (
            reverse("admin:easybookp_availabilityrule_changelist")
            + f"?resource__id__exact={obj.id}"
        )
        return format_html('<a href="{}">Opening hours</a>', url)
    #view_availability_rules_link.short_description = "Правила доступности"

    def view_capacity_windows_link(self, obj):
        if not obj.pk:
            return "-"
        url = (
            reverse("admin:easybook_capacitywindow_changelist")
            + f"?resource__id__exact={obj.id}"
        )
        return format_html('<a href="{}">Variable capacity rules</a>', url)
    #view_capacity_windows_link.short_description = "Окна вместимости"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingForm
    list_display = (
        'user', 
        'resource',
        'is_confirmed', 
        'quantity'
    )
    list_filter = ('resource', 'user')


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = (
        'resource', 
        'weekday', 
        'specific_date', 
        'start_time', 
        'end_time',
        'slot_size'
        )
    list_filter = ('resource',)


@admin.register(CapacityWindow)
class CapacityWindowAdmin(admin.ModelAdmin):
    list_display = ('resource', 'timerange', 'capacity')
    list_filter = ('resource',)


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
        "is_staff",
        "is_active",
    )
    list_filter = (
        "last_name",
        "first_name",
        "email",
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
            "date_of_birth",)}
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
            "is_staff",
            "is_active",
            "groups",
            "user_permissions")}
        ),
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Company)
admin.site.register(Category)