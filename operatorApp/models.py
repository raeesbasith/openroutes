from django.db import models
from guestApp.models import *
from adminApp.models import *
# Create your models here.
class Operator(models.Model):
    operator_id = models.AutoField(primary_key=True)
    operator_name = models.CharField(max_length=100)  
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    license = models.ImageField(upload_to='licenses/')