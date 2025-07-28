# parking/tasks.py

from background_task import background
from .models import Booking, ParkingSlot

@background(schedule=0)
def free_up_parking_slot(booking_id):
    """
    This background task finds an active booking, marks it as completed,
    and sets the corresponding parking slot's status back to 'available'.
    """
    print(f"TASK STARTED: Processing booking ID: {booking_id}")
    try:
        booking = Booking.objects.get(id=booking_id)
        
        # --- CRITICAL FIX ---
        # The status in the model is stored in uppercase (e.g., 'ACTIVE').
        # This check now correctly uses the model's enum for a reliable comparison.
        if booking.status == Booking.BookingStatus.ACTIVE:
            slot = booking.slot
            
            # Update the slot's status and remove the active booking link
            slot.status = ParkingSlot.SlotStatus.AVAILABLE
            slot.active_booking = None
            slot.save()
            
            # Update the booking's status
            booking.status = Booking.BookingStatus.COMPLETED
            booking.save()
            
            print(f"TASK SUCCESS: Slot {slot} is now available. Booking {booking_id} completed.")
        else:
            print(f"TASK SKIPPED: Booking {booking_id} was not in ACTIVE status.")
            
    except Booking.DoesNotExist:
        print(f"TASK FAILED: Booking with ID {booking_id} not found.")
