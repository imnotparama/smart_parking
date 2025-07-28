# parking/forms.py

from django import forms
from .models import Booking, UserProfile
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from decimal import Decimal

class CustomSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))

class BookingForm(forms.ModelForm):
    DURATION_CHOICES = [
        (Decimal('1.00'), '1 Hour'), (Decimal('2.00'), '2 Hours'),
        (Decimal('3.00'), '3 Hours'), (Decimal('4.00'), '4 Hours'),
        (Decimal('5.00'), '5 Hours'), (Decimal('8.00'), '8 Hours (Half Day)'),
        (Decimal('12.00'), '12 Hours (Full Day)'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI / Wallet'), ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'), ('NET_BANKING', 'Net Banking'),
    ]

    duration_hours = forms.TypedChoiceField(
        choices=DURATION_CHOICES, coerce=Decimal,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    slot_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Booking
        fields = [
            'vehicle_number', 'parking_date', 'start_time', 'duration_hours'
        ]
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., TN 01 AB 1234'}),
            'parking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
