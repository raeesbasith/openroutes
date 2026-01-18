from django.db import models
from guestApp.models import *
from adminApp.models import *
from .views import validate_pdf as v
# Create your models here.
class Operator(models.Model):
    operator_id = models.AutoField(primary_key=True)
    operator_name = models.CharField(max_length=100)  
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='requested')
    license = models.FileField(upload_to='operator_licenses/', validators=[v])
    login = models.ForeignKey(login, on_delete=models.CASCADE)