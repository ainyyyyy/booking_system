from rest_framework import serializers
from easybook.models import User, Resource, Booking

class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='userID'
    )

    class Meta:
        model = User
        fields = ["url", "userID", "email", "name", "surname"]

class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='resource-detail',
        lookup_field='resourseID' 
    )

    class Meta:
        model = Resource
        fields = ["url", "resourseID", "name", "description", "schedule"]

class BookingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='booking-detail',
        lookup_field='bookingID'
    )
    user = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='userID',
        queryset=User.objects.all()
    )
    resource = serializers.HyperlinkedRelatedField(
        view_name='resource-detail',
        lookup_field='resourseID', 
        queryset=Resource.objects.all()
    )

    class Meta:
        model = Booking
        fields = ["url", "bookingID", "user", "resource", "start_time", "end_time", "is_confirmed"]