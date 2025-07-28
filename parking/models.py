# parking/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class ParkingSlot(models.Model):
    class SlotStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        OCCUPIED = 'OCCUPIED', 'Occupied'
        MAINTENANCE = 'MAINTENANCE', 'Under Maintenance'

    section = models.CharField(max_length=1, default='A')
    number = models.IntegerField()
    floor = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)
    status = models.CharField(max_length=20, choices=SlotStatus.choices, default=SlotStatus.AVAILABLE)
    active_booking = models.OneToOneField('Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_slot')
    is_handicap = models.BooleanField(default=False)
    is_ev_charging = models.BooleanField(default=False)

    class Meta:
        unique_together = ('floor', 'section', 'number')
        ordering = ['floor', 'section', 'number']

    def __str__(self):
        return f"Slot {self.section}{self.number} (Floor {self.floor})"

class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    booking_id = models.CharField(max_length=10, unique=True, editable=False)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='all_bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    booked_at = models.DateTimeField(auto_now_add=True)
    vehicle_number = models.CharField(max_length=20)
    parking_date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.ACTIVE)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"PK-{str(uuid.uuid4().int)[:6].upper()}"

        start_datetime = timezone.make_aware(datetime.combine(self.parking_date, self.start_time))
        duration_in_minutes = int(float(self.duration_hours) * 60)
        self.end_time = start_datetime + timedelta(minutes=duration_in_minutes)
        self.total_cost = self.slot.price * Decimal(self.duration_hours)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_id} by {self.user.username}"