from django import forms
from .models import Booking, ParkingSlot

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['vehicle_number', 'slot']