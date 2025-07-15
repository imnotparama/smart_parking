from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

# ------------------------
# USER PROFILE MODEL
# ------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

# ------------------------
# PARKING SLOT MODEL
# ------------------------
class ParkingSlot(models.Model):
    section = models.CharField(max_length=1, default='A')
    number = models.IntegerField()
    floor = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)
    is_available = models.BooleanField(default=True)
    is_handicap = models.BooleanField(default=False)
    is_ev_charging = models.BooleanField(default=False)

    class Meta:
        unique_together = ('floor', 'section', 'number')
        ordering = ['floor', 'section', 'number']

    def __str__(self):
        return f"Slot {self.section}{self.number} (Floor {self.floor})"

# ------------------------
# BOOKING MODEL
# ------------------------
class Booking(models.Model):
    # ✅ MODIFIED: Added status choices for better state management
    class BookingStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    booked_at = models.DateTimeField(auto_now_add=True)
    vehicle_number = models.CharField(max_length=20)
    parking_date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.IntegerField(default=1)
    
    # ✅ NEW: Calculated end time for automated status updates
    end_time = models.DateTimeField(null=True, blank=True, help_text="Automatically calculated on save")
    
    # ✅ MODIFIED: Replaced is_active boolean with a more descriptive status field
    status = models.CharField(max_length=10, choices=BookingStatus.choices, default=BookingStatus.ACTIVE)

    def save(self, *args, **kwargs):
        # ✅ NEW: Automatically calculate the end_time when a booking is first created
        if not self.pk: # Only on creation
            start_datetime = timezone.make_aware(datetime.combine(self.parking_date, self.start_time))
            self.end_time = start_datetime + timezone.timedelta(hours=self.duration_hours)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} booked {self.slot} on {self.parking_date}"