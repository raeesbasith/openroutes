from django.db import models
from guestApp.models import login
from adminApp.models import Location
# Create your models here.
class OperatorProfile(models.Model):
    user = models.OneToOneField(login, on_delete=models.CASCADE)
    agency_name = models.CharField(max_length=50)
    description = models.TextField()
    contact_no = models.IntegerField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    verification_status = models.CharField(max_length=10, default="PENDING")
    subscription_plan = models.CharField(max_length=10, default="FREE")