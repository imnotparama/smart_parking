import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from django.contrib.auth.models import User
from parking.models import ParkingSlot, Booking

# Create superuser
user, created = User.objects.get_or_create(username='admin', email='admin@example.com')
if created:
    user.set_password('admin123')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("Superuser created")

# Create a regular user
john, created = User.objects.get_or_create(username='john_doe', email='john@example.com')
if created:
    john.set_password('password123')
    john.save()
    print("User john_doe created")

# Make sure slots exist
if not ParkingSlot.objects.exists():
    for section in ['A', 'B']:
        for i in range(1, 11):
            ParkingSlot.objects.create(floor=1, section=section, number=i, price=50.0)
    print("Slots created")

# Create some bookings
slots = list(ParkingSlot.objects.all())
now = timezone.now()

if Booking.objects.count() == 0:
    for i in range(15):
        slot = slots[i % len(slots)]
        b = Booking.objects.create(
            user=user if i % 2 == 0 else john,
            slot=slot,
            vehicle_number=f"AB12CD{3456+i}",
            parking_date=now.date() - timedelta(days=i%6),
            start_time=(now - timedelta(hours=i)).time(),
            duration_hours=2,
            total_cost=slot.price * 2,
            status='COMPLETED'
        )
    print("Bookings created")
