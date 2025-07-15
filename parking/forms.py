# In parking/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class BookingForm(forms.Form):
    vehicle_number = forms.CharField(label="Vehicle Number", widget=forms.TextInput(attrs={'placeholder': 'e.g., KA-01-AB-1234'}))
    parking_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    
    # ✅ MODIFIED: Changed from ChoiceField to TypedChoiceField with coerce=int
    # This is the fix. It ensures the form output is an integer, not a string.
    duration = forms.TypedChoiceField(
        label="Duration (Hours)",
        choices=[(i, f"{i} Hours") for i in range(1, 9)],
        coerce=int  # This converts the submitted string value to an integer
    )
    
    payment_method = forms.ChoiceField(choices=[('upi', 'UPI'), ('card', 'Credit/Debit Card')])
    slot_id = forms.IntegerField(widget=forms.HiddenInput())

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
            # Check if a profile already exists to avoid errors on user update
            UserProfile.objects.get_or_create(user=user, defaults={'phone_number': self.cleaned_data['phone_number']})
        return user

class CustomLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))