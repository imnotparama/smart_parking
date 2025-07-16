# parking/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile
from decimal import Decimal

class BookingForm(forms.Form):
    slot_id = forms.IntegerField(widget=forms.HiddenInput())

    vehicle_number = forms.CharField(
        label="Vehicle Number",
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., TN-01-AB-1234'})
    )
    parking_date = forms.DateField(
        label="Parking date",
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().strftime('%Y-%m-%d')})
    )
    start_time = forms.TimeField(
        label="Start time",
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    
    # --- UPGRADE: New duration choices in 30-minute intervals ---
    # Generates choices from 0.5 hours to 8.0 hours
    DURATION_CHOICES = [(f"{i * 0.5}", f"{i * 0.5} Hours") for i in range(1, 17)]
    duration = forms.TypedChoiceField(
        label="Duration",
        choices=DURATION_CHOICES,
        coerce=Decimal, # Ensures the form data is a Decimal
        initial='1.0'
    )
    
    payment_method = forms.ChoiceField(
        label="Payment method",
        choices=[('UPI', 'UPI'), ('CARD', 'Credit/Debit Card')],
        initial='UPI'
    )

class CustomSignupForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True, label="Phone Number")
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'phone_number': self.cleaned_data['phone_number']})
        return user

class CustomLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
