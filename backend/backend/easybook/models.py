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
    

class Company(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, unique=True)
    logo = models.ImageField(upload_to='media', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'easybook'
        indexes = [
            models.Index(fields=('is_active',)),
        ]
        """constraints = [
            models.UniqueConstraint(fields=['url'], name='uniq_company_url'),
        ]
"""
    def __str__(self) -> str:
        return self.name


class CompanyMembership(models.Model):
    """
    Модель для связи компаний и пользоватей
    """
    class Meta:
        app_label = 'easybook'
        constraints = [
            models.UniqueConstraint(fields=['company', 'user'], name='uniq_company_user_membership'),
        ]
        indexes = [
            models.Index(fields=('company', 'is_active')),
            models.Index(fields=('company', 'role')),
        ]

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        STAFF = "staff", "Staff"
        
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.STAFF
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.user} @ {self.company} ({self.role})'
    

class Staff(models.Model):
    class Meta:
        app_label = 'easybook'
        indexes = [
            models.Index(fields=('company', 'is_active')),
            #models.Index(fields=('company', 'display_name')),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'user'],
                name='uniq_company_user_as_staff',
                condition=Q(user__isnull=False)
            ),
        ]

    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='staff'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='staff_profiles',
        null=True,
        blank=True,
    )
    display_name = models.CharField(max_length=100)
    company_email = models.EmailField(null=True, blank=True)
    company_phone = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.display_name} ({self.company})'


class Resource(models.Model):
    """
    Базовая сущность, которую можно бронировать.
    """
    class Meta:
        app_label = 'easybook'
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'name'], 
                name='uniq_resource_name_per_company'
            ),
        ]
        indexes = [
            models.Index(fields=('company',)),
            #models.Index(fields=('company', 'name')),
            #models.Index(fields=('company', 'max_capacity')),
        ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='resources',
        null=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_resources',
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    url = models.URLField(blank=True)
    # если >1 — один и тот же слот могут занимать несколько человек
    max_capacity = models.PositiveIntegerField(default=1)
    requires_staff = models.BooleanField(default=False)
    
    # Список сотрудников, которые оказывают услугу
    staff_members = models.ManyToManyField(
        Staff,
        through='ResourceStaff',
        related_name='resources',
        blank=True
    )

    def __str__(self) -> str:
        return self.name
    

class ResourceStaff(models.Model):
    class Meta:
        app_label = 'easybook'
        constraints = [
            models.UniqueConstraint(
                fields=['resource', 'staff'], 
                name='uniq_resource_staff_pair'
            ),
        ]
        indexes = [
            models.Index(fields=('resource',)),
            models.Index(fields=('staff',)),
        ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)

    def clean(self):
        if self.resource.company != self.staff.company:
            raise ValidationError(
                'Resource and Staff must belong to the same Company.'
            )

    def __str__(self) -> str:
        return f'{self.resource} — {self.staff}'


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

        - Если есть хотя бы одно правило на конкретную дату
               — возвращаем только их.
        - Иначе — weekly-rules.
        """
        qs = self.for_resource(resource).for_day(day)
        if qs and qs.first().priority == 0:
            return qs.filter(priority=0)
        return qs  
        

class AvailabilityRuleManager(models.Manager):
    def get_queryset(self):
        return AvailabilityRuleQuerySet(self.model, using=self._db)

    def effective_for_day(self, resource, day):
        return self.get_queryset().effective_for_day(resource, day)


class AvailabilityRule(models.Model):
    """
    Определяет, когда услуга доступна и какой длины слот
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


# TODO: Добавить переменную capacity для отдельных сотрудников
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
                name='prevent_overlap_for_the_same_user_and_resource',
                expressions=(
                    ('user', '='),
                    ('resource', '='),
                    ('timerange', '&&'),
                ),
            ),
            ExclusionConstraint(
                name='prevent_staff_double_booking',
                expressions=(
                    ('staff', '='),
                    ('timerange', '&&'),
                ),
                condition=Q(staff__isnull=False),
            ),
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
    staff = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        related_name='bookings',
        null=True,
        blank=True,
    )
    timerange = DateTimeRangeField(null=True, blank=True)  # хранит [start, end)
    is_confirmed = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)  # сколько мест из capacity заняли
    additional_info = models.TextField(blank=True, null=True)
    def clean(self):
        """if self.timerange is None or self.timerange.start is None or self.timerange.end is None:
            raise ValidationError('`timerange` must be set with both start and end times.')
        if self.timerange.lower >= self.timerange.upper:
            raise ValidationError('`timerange.start` must be less than `timerange.end`.')
"""
        # Если ресурс требует выбора сотрудника — staff обязателен
        if self.resource.requires_staff and not self.staff:
            raise ValidationError(
                'This resource requires selecting a staff member.'
            )

        # Если указан сотрудник — он должен быть из той же компании 
        if self.staff:
            if self.resource.company != self.staff.company:
                raise ValidationError(
                    'Selected staff must belong to the same company' \
                    ' as the resource.'
                    )
            # Проверка принадлежности сотрудника к услуге
            if not ResourceStaff.objects.filter(
                resource_id=self.resource, 
                staff_id=self.staff
            ).exists():
                raise ValidationError(
                    'Selected staff is not assigned to this resource.'
                )
            
    def __str__(self) -> str:
        base = f'{self.resource}: {self.timerange} by {self.user}'
        if self.staff:
            base += f' (staff: {self.staff.display_name})'
        return base