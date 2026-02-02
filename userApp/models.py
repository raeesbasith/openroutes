from django.db import models
from guestApp.models import *
from adminApp.models import *
from operatorApp.models import *
# Create your models here.

class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    traveller = models.ForeignKey(TravellerProfile, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    tour_date = models.DateField()
    total_persons = models.IntegerField()
    persons_needing_accessibility = models.IntegerField(default=0, null=True)
    caregiver_gender_preference = models.CharField(max_length=10, null=True, blank=True)
    base_amount = models.FloatField()
    accessibility_amount = models.FloatField(default=0.0)
    total_amount = models.FloatField()
    booking_status = models.CharField(max_length=20, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)

class BookingAccessibility(models.Model):
    booking_acc_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    accessibility = models.ForeignKey(Accessibility, on_delete=models.CASCADE)

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50) 
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='success')
