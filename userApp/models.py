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
    commission_amount = models.FloatField(default=0.0)
    booking_status = models.CharField(max_length=20, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    cancellation_requested_at = models.DateTimeField(null=True, blank=True)
    refund_amount = models.FloatField(default=0.0)
    refund_processed_at = models.DateTimeField(null=True, blank=True)
    refund_notes = models.TextField(null=True, blank=True)

    @property
    def net_amount(self):
        return self.effective_total_amount - self.effective_commission_amount

    @property
    def effective_total_amount(self):
        if self.booking_status == 'cancelled':
            return 0.0
        realization = self.total_amount - self.refund_amount
        return realization if realization > 0 else 0.0

    @property
    def effective_commission_amount(self):
        if self.total_amount <= 0:
            return 0.0
        commission_rate = self.commission_amount / self.total_amount if self.total_amount else 0
        effective_commission = self.effective_total_amount * commission_rate
        return effective_commission if effective_commission > 0 else 0.0

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

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    traveller = models.ForeignKey(TravellerProfile, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
