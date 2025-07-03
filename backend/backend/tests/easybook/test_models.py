from datetime import datetime, time, date
import pytest
from easybook.models import AvailabilityRule, User, Resource
from django.core.exceptions import ValidationError


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
def test_create_weekly_rule(user):
    resource = Resource.objects.create(
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
def test_create_rule_with_equal_start_and_end_time(user):
    resource = Resource.objects.create(user=user, name="Conference Room B")

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
def test_validation_fails_both_weekday_and_specific_date_set(user):
    resource = Resource.objects.create(user=user, name="Test Resource")
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
def test_cascade_deletion_removes_rules(user):
    resource = Resource.objects.create(user=user, name='Test Resource')
    rule = AvailabilityRule.objects.create(
        resource=resource,
        weekday=1,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    resource.delete()
    assert not AvailabilityRule.objects.filter(pk=rule.pk).exists()
