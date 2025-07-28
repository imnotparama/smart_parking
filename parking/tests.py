from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import ParkingSlot, Booking
from django.utils import timezone
from datetime import date, time

class BookingFlowTestCase(TestCase):
    def setUp(self):
        """Set up a test user and a parking slot for all tests."""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.slot = ParkingSlot.objects.create(section='A', number=1, floor=1, price=50.00)

    def test_booking_creation_and_status_change(self):
        """
        Test that a user can book a slot, and the slot's status changes correctly.
        """
        self.client.login(username='testuser', password='testpassword')
        
        # Check that the slot is initially available
        self.assertEqual(self.slot.status, ParkingSlot.SlotStatus.AVAILABLE)

        # POST data to book the slot
        booking_data = {
            'slot_id': self.slot.id,
            'vehicle_number': 'TEST-1234',
            'parking_date': date.today(),
            'start_time': time(14, 0), # 2 PM
            'duration': '1.0',
            'payment_method': 'UPI',
        }
        
        response = self.client.post(reverse('parking:book_slot'), booking_data)
        
        # Check that the user is redirected to the 'my_bookings' page
        self.assertRedirects(response, reverse('parking:my_bookings'))
        
        # Refresh the slot from the database to get its updated state
        self.slot.refresh_from_db()
        
        # Check that the slot is now occupied
        self.assertEqual(self.slot.status, ParkingSlot.SlotStatus.OCCUPIED)
        
        # Check that a booking was created
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.slot, self.slot)
        self.assertEqual(booking.status, Booking.BookingStatus.ACTIVE)