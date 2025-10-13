from datetime import datetime, time, date
import pytest
from easybook.models import CapacityWindow, AvailabilityRule, Booking, Resource, Company
from django.core.exceptions import ValidationError
#from psycopg2.extras import DateTimeTZRange
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware
from django.db.backends.postgresql.psycopg_any import DateTimeTZRange

@pytest.mark.django_db
def test_user(user):
    """
    user = User.objects.create(
        email="am@g.com",
        password="123",
        first_name="Vyacheslav",
        last_name="Konischev"
    )"""
    assert user.email == "am@g.com"
    assert user.first_name == "Vyacheslav"
    assert user.last_name == "Konischev"

@pytest.mark.django_db
def test_create_weekly_rule(user, company):
    resource = Resource.objects.create(
        company=company,
        user=user,
        name="Coworking",
        description="The best coworking in the world"
    )

    rule = AvailabilityRule.objects.create(
        resource=resource,
        weekday=0,
        start_time=time(10, 0),
        end_time=time(18, 0),
        slot_size=60
    )
    
    rule.clean()
    rule.save()    
       
    saved_rule = AvailabilityRule.objects.get(pk=rule.pk)

    assert saved_rule.weekday == 0
    assert saved_rule.specific_date is None
    assert saved_rule.start_time == time(10, 0)
    assert saved_rule.end_time == time(18, 0)
    assert saved_rule.slot_size == 60
    assert str(saved_rule).startswith(f'Rule {rule.pk}: wd=0 10:00:00-18:00:00')

@pytest.mark.django_db
def test_create_rule_with_equal_start_and_end_time(resource):
    with pytest.raises(ValidationError) as excinfo:
        rule = AvailabilityRule(
            resource=resource,
            weekday=3,
            start_time=time(14, 0),
            end_time=time(14, 0),
            slot_size=30
        )
        rule.clean()  

    assert "`start_time` must be less than `end_time`." in str(excinfo.value)

@pytest.mark.django_db
def test_validation_fails_both_weekday_and_specific_date_set(resource):
    rule = AvailabilityRule(
        resource=resource,
        weekday=1,
        specific_date=date(2025, 7, 15),
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    with pytest.raises(
        ValidationError, 
        match='Either `weekday` OR `specific_date` must be set'
        ):
        rule.clean()

@pytest.mark.django_db
def test_cascade_deletion_removes_rules(resource):
    rule = AvailabilityRule.objects.create(
        resource=resource,
        weekday=1,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    resource.delete()
    assert not AvailabilityRule.objects.filter(pk=rule.pk).exists()

@pytest.mark.django_db
def test_specific_date_priority(user, resource):
    rule1 = AvailabilityRule.objects.create(
        resource=resource,
        specific_date=date(2025, 7, 19),
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    rule2 = AvailabilityRule.objects.create(
        resource=resource,
        weekday=5,
        start_time=time(10, 0),
        end_time=time(18, 0),
        slot_size=60
    )
    rule1.clean()
    rule2.clean()
    
    day = date(2025, 7, 19)
    rules = AvailabilityRule.objects.effective_for_day(resource, day)

    assert rules[0].start_time == time(9, 0)

@pytest.mark.django_db(transaction=True)
def test_capacity_window_exclusion_constraint(resource, other_resource):
    start1 = make_aware(datetime(2025, 1, 1, 10, 0))
    end1 = make_aware(datetime(2025, 1, 1, 12, 0))
    range1 = DateTimeTZRange(start1, end1)

    CapacityWindow.objects.create(
        resource=resource, 
        timerange=range1, 
        capacity=5
    )

    start2_overlap = make_aware(datetime(2025, 1, 1, 11, 0))
    end2_overlap = make_aware(datetime(2025, 1, 1, 13, 0))
    range2_overlap = DateTimeTZRange(start2_overlap, end2_overlap)

    with pytest.raises(IntegrityError) as excinfo:
        CapacityWindow.objects.create(
            resource=resource, 
            timerange=range2_overlap, 
            capacity=8
        )

    assert 'prevent_capacity_windows_overlap' in str(excinfo.value).lower()

    start3_adjacent = make_aware(datetime(2025, 1, 1, 12, 0))
    end3_adjacent = make_aware(datetime(2025, 1, 1, 14, 0))
    range3_adjacent = DateTimeTZRange(start3_adjacent, end3_adjacent)

    try:
        CapacityWindow.objects.create(
            resource=resource, 
            timerange=range3_adjacent, 
            capacity=12
        )
    except IntegrityError:
        pytest.fail(
            "Создание примыкающего CapacityWindow " \
            "не должно вызывать IntegrityError."
        )

    assert CapacityWindow.objects.filter(resource=resource).count() == 2

    try:
        CapacityWindow.objects.create(
            resource=other_resource, 
            timerange=range2_overlap, 
            capacity=15
        )
    except IntegrityError:
        pytest.fail(
            "Создание пересекающегося CapacityWindow " \
            "для другого ресурса не должно вызывать IntegrityError."
        )

    assert CapacityWindow.objects.count() == 3
    assert CapacityWindow.objects.filter(resource=other_resource).count() == 1

@pytest.mark.django_db(transaction=True)
def test_booking_exclusion_constraint(user, resource, other_resource):
    start1 = make_aware(datetime(2025, 1, 1, 10, 0))
    end1 = make_aware(datetime(2025, 1, 1, 12, 0))
    range1 = DateTimeTZRange(start1, end1)

    Booking.objects.create(
        user=user,
        resource=resource, 
        timerange=range1, 
    )

    start2_overlap = make_aware(datetime(2025, 1, 1, 11, 0))
    end2_overlap = make_aware(datetime(2025, 1, 1, 13, 0))
    range2_overlap = DateTimeTZRange(start2_overlap, end2_overlap)

    with pytest.raises(IntegrityError) as excinfo:
        Booking.objects.create(
            user=user,
            resource=resource, 
            timerange=range2_overlap,
        )

    assert 'prevent_overlap_for_the_same_user' in str(excinfo.value).lower()

    try:
        Booking.objects.create(
            user=user,
            resource=other_resource, 
            timerange=range2_overlap, 
        )
    except IntegrityError:
        pytest.fail(
            "Создание примыкающего Booking для другого ресурса" \
            " не должно вызывать IntegrityError."
        )

@pytest.mark.django_db
def test_booking_validation_fails_staff_not_assigned(
    user, 
    resource, 
    staff
):
    start = make_aware(datetime(2025, 1, 1, 10, 0))
    end = make_aware(datetime(2025, 1, 1, 12, 0))
    rng = DateTimeTZRange(start, end)

    booking = Booking.objects.create(
        user=user,
        resource=resource,
        staff=staff,
        timerange=rng, 
    )

    with pytest.raises(ValidationError) as excinfo:
        booking.clean()
    
    assert 'Selected staff is not assigned to this resource.' in str(excinfo.value)

@pytest.mark.django_db
def test_validation_fails_staff_from_another_company(
    user, 
    resource, 
    other_company_staff
):
    start = make_aware(datetime(2025, 1, 1, 10, 0))
    end = make_aware(datetime(2025, 1, 1, 12, 0))
    rng = DateTimeTZRange(start, end)

    booking = Booking.objects.create(
        user=user,
        resource=resource,
        staff=other_company_staff,
        timerange=rng, 
    )

    with pytest.raises(ValidationError) as excinfo:
        booking.clean()
    
    assert 'Selected staff must belong to the same company' in str(excinfo.value)
