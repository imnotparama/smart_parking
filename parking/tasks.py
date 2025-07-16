# bookings/tasks.py
# This is a new file you need to create.

from background_task import background
from .models import Booking

# The @background decorator turns this function into a background task
# We will schedule it from the view when a booking is created.
@background(schedule=0)
def free_up_parking_slot(booking_id):
    """
    This background task finds a booking, marks it as completed,
    and sets the corresponding parking slot's status back to 'available'.
    """
    print(f"TASK STARTED: Attempting to process booking ID: {booking_id}")
    try:
        # Get the specific booking that needs to be processed
        booking = Booking.objects.get(id=booking_id)
        
        # It's good practice to check if the booking is still 'active'.
        # This prevents errors if it was, for example, manually cancelled.
        if booking.status == 'active':
            slot = booking.parking_slot
            
            # --- Main Logic ---
            # 1. Update the slot's status and remove the link to the active booking
            slot.status = 'available'
            slot.active_booking = None
            slot.save()
            
            # 2. Update the booking's status to 'completed'
            booking.status = 'completed'
            booking.save()
            
            print(f"TASK SUCCESS: Slot {slot.slot_id} is now available. Booking {booking_id} completed.")
        else:
            print(f"TASK SKIPPED: Booking {booking_id} was already in status '{booking.status}'. No action taken.")
            
    except Booking.DoesNotExist:
        print(f"TASK FAILED: Booking with ID {booking_id} not found.")