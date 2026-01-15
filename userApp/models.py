from django.db import models
from guestApp.models import *
from adminApp.models import *
# Create your models here.
class TravellerProfile(models.Model):
    traveller_id = models.AutoField(primary_key=True)
    traveller_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    login = models.ForeignKey(login, on_delete=models.CASCADE)
    reg_date = models.DateTimeField(auto_now_add=True)