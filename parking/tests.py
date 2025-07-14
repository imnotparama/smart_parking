from django.test import Client, TestCase
from django.contrib.auth.models import User
from .models import ParkingSlot, Booking


class BookingFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("parama", "p@example.com", "pass123")
        self.slot = ParkingSlot.objects.create(number=1, floor=0)

    def test_user_can_book_and_cancel(self):
        self.client.login(username="parama", password="pass123")

        # Book
        self.client.post(f"/book/{self.slot.id}/")
        self.slot.refresh_from_db()
        self.assertFalse(self.slot.is_available)

        # Cancel
        self.client.post(f"/cancel/{self.slot.id}/")
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_available)
