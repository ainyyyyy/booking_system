from django.db import models
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import ValidationError
from django.db.models import Case, When, IntegerField, Q
from django.conf import settings
from django.contrib.auth.models import AbstractUser
#from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


"""
Migration sequence:
- 0001_initial: comment every constraint
- 0002: Create empty + Add extension
- 0003: Uncomment constraints
- 0004: Create empty + Add trigger
"""

"""
0002:

from django.contrib.postgres.operations import BtreeGistExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('easybook', '0001_initial'),
    ]

    operations = [
        BtreeGistExtension(),
    ]

"""

"""
0004:


"""

"""class User(models.Model):
    class Meta:
        app_label = 'easybook'

    email = models.EmailField(unique=True, max_length=254)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f'{self.name} {self.surname}'.strip()"""


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        email, 
        password,
        **extra_fields
        ):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email) # lowercase the domain
        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password) # hash raw password and set
        user.save()
        return user
    
    def create_superuser(
        self,
        email, 
        password,
        **extra_fields
        ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )
        return self.create_user(
            email, 
            password,
            **extra_fields
        )


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    organization_name = models.CharField(max_length=100, null=True, blank=True)
    organization_description = models.TextField(null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    def __str__(self):
        return self.email
    

class Resource(models.Model):
    """
    Базовая сущность, которую можно бронировать.
    """
    class Meta:
        app_label = 'easybook'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    site = models.URLField(blank=True)
    # если >1 — один и тот же слот могут занимать несколько человек
    max_capacity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return self.name


class AvailabilityRuleQuerySet(models.QuerySet):
    def for_resource(self, resource):
        return self.filter(resource=resource)

    def for_day(self, day):
        """
        Возвращает все правила для конкретной даты
        """
        return (
            self.filter(
                Q(specific_date=day) |
                Q(specific_date__isnull=True, weekday=day.weekday())
            )
            .annotate(
                priority=Case(
                    When(specific_date=day, then=0),
                    default=1,
                    output_field=IntegerField(),
                )
            )
            .order_by('priority', 'start_time')  # сортировка по приоритету
        )

    def effective_for_day(self, resource, day):
        """
        Итоговые правила, которые действуют в определенный день.

        Алгоритм:
            1. Если есть хотя бы одно правило на конкретную дату
               — возвращаем только их.
            2. Иначе — weekly-rules.
        """
        qs = self.for_resource(resource).for_day(day)
        if qs and qs.first().priority == 0:
            return qs.filter(priority=0)
        return qs  
        

class AvailabilityRuleManager(models.Manager):
    def get_queryset(self):
        return AvailabilityRuleQuerySet(self.model, using=self._db)

    # фасад к основной функции, чтобы вызывать прямо так:
    # AvailabilityRule.objects.effective_for_day(resource, date)
    def effective_for_day(self, resource, day):
        return self.get_queryset().effective_for_day(resource, day)


class AvailabilityRule(models.Model):
    """
    Определяет, когда сервис доступен и какой длины слот
    """
    class Meta:
        app_label = 'easybook'
        indexes = [
            models.Index(fields=('weekday',)),
            models.Index(fields=('specific_date',)),
        ]

    resource = models.ForeignKey(
        Resource, 
        on_delete=models.CASCADE, 
        related_name='availability_rules'
    )

    # Если правило повторяющееся — храним день недели (0..6). 
    # Если разовое - оставляем null и заполняем specific_date.
    weekday = models.PositiveSmallIntegerField(null=True, blank=True)
    specific_date = models.DateField(null=True, blank=True)

    start_time = models.TimeField()
    end_time = models.TimeField()

    # Длина одного слота в минутах. 0 или null => 
    # => произвольный интервал (user вводит начало/конец сам).
    slot_size = models.PositiveIntegerField(null=True, blank=True)

    objects = AvailabilityRuleManager()

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(
                '`start_time` must be less than `end_time`.'
                )
        if bool(self.weekday is not None) == bool(self.specific_date):
            raise ValidationError(
                'Either `weekday` OR `specific_date` must be set (exclusively).'
            )

    def __str__(self) -> str:
        if self.weekday is not None:
            return f'Rule {self.pk}: wd={self.weekday} {self.start_time}-{self.end_time}'
        return f'Rule {self.pk}: {self.specific_date} {self.start_time}-{self.end_time}'


class CapacityWindow(models.Model):
    """
    Задаёт вместимость `capacity` на конкретный интервал времени.
    Если окна не заданы, действует Resource.max_capacity.
    """
    class Meta:
        app_label = 'easybook'
        indexes = [GistIndex(fields=('timerange',))]
        # Не допускаем пересечения окон на одном ресурсе, 
        # чтобы емкость была однозначной
        constraints = [
            ExclusionConstraint(
                name='prevent_capacity_windows_overlap',
                expressions=(
                    ('resource', '='),
                    ('timerange', '&&'),
                ),
            )
        ]

    resource = models.ForeignKey(
        Resource, 
        on_delete=models.CASCADE, 
        related_name='capacity_windows'
    )
    timerange = DateTimeRangeField(null=True, blank=True) # [start, end)
    capacity  = models.PositiveIntegerField()         

    def __str__(self):
        return f'{self.resource} {self.timerange} ({self.capacity})'


class Booking(models.Model):
    class Meta:
        app_label = 'easybook'
        indexes = [
            GistIndex(fields=('timerange',)),  # ускоряет проверку пересечений
        ]
        constraints = [
            ExclusionConstraint(
                name='prevent_overlap_for_the_same_user',
                expressions=(
                    ('user', '='),
                    ('resource', '='),
                    ('timerange', '&&'),
                ),
            )
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    resource = models.ForeignKey(
        Resource, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )

    timerange = DateTimeRangeField(null=True, blank=True)  # хранит [start, end)

    is_confirmed = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)  # сколько мест из capacity заняли

    additional_info = models.TextField(blank=True, null=True)
    """def clean(self):
        if self.timerange is None or self.timerange.start is None or self.timerange.end is None:
            raise ValidationError('`timerange` must be set with both start and end times.')
        if self.timerange.lower >= self.timerange.upper:
            raise ValidationError('`timerange.start` must be less than `timerange.end`.')
"""
    def __str__(self) -> str:
        return f'{self.resource}: {self.timerange} by {self.user}'
