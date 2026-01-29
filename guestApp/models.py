from django.db import models
from adminApp.models import District

# Create your models here.
class login(models.Model):
    login_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    role = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='active')

class Operator(models.Model):
    operator_id = models.AutoField(primary_key=True)
    operator_name = models.CharField(max_length=100)  
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='requested')
    license = models.FileField(upload_to='operator_licenses/')
    login = models.ForeignKey(login, on_delete=models.CASCADE)

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
