# parking/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    
    def __str__(self):
        return self.user.username

# This single signal handles both creating and updating the profile
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
# This signal automatically creates a UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


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
        return f"F{self.floor} - {self.section}{self.number}"

class Booking(models.Model):
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    vehicle_number = models.CharField(max_length=20)
    parking_date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} booked {self.slot}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username