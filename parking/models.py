from django.db import models
from django.contrib.auth.models import User

class ParkingSlot(models.Model):
    number = models.IntegerField(unique=True)
    is_available = models.BooleanField(default=True)

class Booking(models.Model):
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)