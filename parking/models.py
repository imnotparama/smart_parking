from django.db import models
from django.contrib.auth.models import User

class ParkingSlot(models.Model):
    number = models.IntegerField()
    floor = models.IntegerField()  # or models.CharField(max_length=10) for names like "G", "1", "2"
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Slot {self.number} (Floor {self.floor})"
class Booking(models.Model):
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)