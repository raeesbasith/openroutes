from django.db import models
from django.core.exceptions import ValidationError
from guestApp.models import *
from adminApp.models import *

# Create your models here.

class Tour(models.Model):
    tour_id = models.AutoField(primary_key=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    tour_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    duration_days = models.IntegerField()
    max_persons = models.IntegerField()
    tour_itinerary = models.FileField(upload_to='tour_itineraries/', null=True)
    status = models.CharField(max_length=20, default='available')
    created_at = models.DateTimeField(auto_now_add=True)

class TourAccessibility(models.Model):
    tour_acc_id = models.AutoField(primary_key=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    accessibility = models.ForeignKey(Accessibility, on_delete=models.CASCADE)

class TourImages(models.Model):
    tour_image_id = models.AutoField(primary_key=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tour_images/')
    