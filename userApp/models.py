from django.db import models
from guestApp.models import login
# Create your models here.
class TravellerProfile(models.Model):
    user = models.OneToOneField(login, on_delete=models.CASCADE)
    disability_type = models.CharField(max_length=50)
    address = models.TextField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)