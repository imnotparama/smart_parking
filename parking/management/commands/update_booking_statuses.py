# In parking/management/commands/update_booking_statuses.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from parking.models import Booking, ParkingSlot

class Command(BaseCommand):
    help = 'Checks for active bookings whose end time has passed and updates their status to COMPLETED.'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        self.stdout.write(f"[{now}] Running update_booking_statuses command...")

        # Find active bookings that have ended
        expired_bookings = Booking.objects.filter(
            status=Booking.BookingStatus.ACTIVE,
            end_time__lte=now
        )
        
        count = expired_bookings.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No expired bookings found. All statuses are up to date."))
            return

        self.stdout.write(f"Found {count} expired booking(s) to update.")

        for booking in expired_bookings:
            # Update booking status to COMPLETED
            booking.status = Booking.BookingStatus.COMPLETED
            booking.save()

            # Make the associated parking slot available again
            slot = booking.slot
            slot.is_available = True
            slot.save()
            
            self.stdout.write(f"Updated booking ID {booking.id} for user '{booking.user.username}'. Slot {slot} is now available.")

        self.stdout.write(self.style.SUCCESS(f"Successfully processed and updated {count} booking(s)."))