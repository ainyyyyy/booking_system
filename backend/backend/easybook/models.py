from django.db import models

class User(models.Model):
    email = models.CharField(max_length=50)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    
    def __str__(self):
        return self.email


class Resource(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    schedule = models.JSONField()  
    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)
    #def __str__(self):
    #    return self.name
