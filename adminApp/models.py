from django.db import models

# Create your models here.
class District(models.Model):
    district_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    
class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    district_id = models.ForeignKey(District, on_delete=models.CASCADE)