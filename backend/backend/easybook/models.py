
from django.db import models
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import ValidationError
from django.db.models import Case, When, IntegerField, Q

class User(models.Model):
    class Meta:
        app_label = 'easybook'

    email = models.EmailField(unique=True, max_length=254)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f'{self.name} {self.surname}'.strip()


class Resource(models.Model):
    """
    Базовая сущность, которую можно бронировать.
    """
    class Meta:
        app_label = 'easybook'

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
        return qs  # останутся только weekly
        

class AvailabilityRuleManager(models.Manager):
    def get_queryset(self):
        return AvailabilityRuleQuerySet(self.model, using=self._db)

    # фасад к основной функции, чтобы вызывать прямо так:
    # AvailabilityRule.objects.effective_for_day(resource, date)
    def effective_for_day(self, resource, day):
        return self.get_queryset().effective_for_day(resource, day)


class AvailabilityRule(models.Model):
    """
    Определяет, когда ресурс открыт и какой длины слот.
    Примеры:
        • каждая среда с 10:00 до 18:00, продолжительность слота 60 мин
        • единовременное окно 14.06.2025 09:00–13:00, продолжительность слота 30 мин
    """
    class Meta:
        app_label = 'easybook'
        indexes = [
            models.Index(fields=('weekday',)),
            models.Index(fields=('specific_date',)),
        ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='availability_rules')

    # Если правило повторяющееся — храним weekday (0..6). Если разовое - оставляем null и заполняем date.
    weekday = models.PositiveSmallIntegerField(null=True, blank=True)
    specific_date = models.DateField(null=True, blank=True)

    start_time = models.TimeField()
    end_time = models.TimeField()

    # Длина одного слота в минутах. 0 или null => произвольный интервал (user вводит начало/конец сам).
    slot_size = models.PositiveIntegerField(null=True, blank=True)

    objects = AvailabilityRuleManager()

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('`start_time` must be less than `end_time`.')
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
    Если пересекающихся окон нет, действует Resource.max_capacity.
    """
    class Meta:
        app_label = 'easybook'
        indexes = [GistIndex(fields=('timerange',))]
        # Не допускаем пересечения окон на одном ресурсе, чтобы емкость была однозначной
        constraints = [
            ExclusionConstraint(
                name='prevent_capacity_windows_overlap',
                expressions=(
                    ('resource', '='),
                    ('timerange', '&&'),
                ),
            )
        ]

    resource = models.ForeignKey('Resource', on_delete=models.CASCADE, related_name='capacity_windows')
    timerange = DateTimeRangeField(null=True, blank=True)                  # [start, end)
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings')

    timerange = DateTimeRangeField(null=True, blank=True)  # хранит [start, end)

    is_confirmed = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)  # сколько мест из capacity заняли

    def __str__(self) -> str:
        return f'{self.resource}: {self.timerange} by {self.user}'
