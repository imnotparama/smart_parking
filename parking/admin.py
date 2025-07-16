# parking/admin.py

from django.contrib import admin
from .models import UserProfile, ParkingSlot, Booking

# Register your models here.

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ParkingSlot model.
    """
    # Replaced 'is_available' with 'status'
    list_display = ('__str__', 'status', 'floor', 'price', 'is_handicap', 'active_booking')
    
    # Replaced 'is_available' with 'status'
    list_filter = ('floor', 'status', 'is_handicap', 'is_ev_charging')
    
    search_fields = ('section', 'number')
    list_per_page = 20

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Booking model.
    """
    list_display = ('id', 'user', 'slot', 'status', 'vehicle_number', 'end_time')
    list_filter = ('status', 'parking_date', 'user')
    search_fields = ('vehicle_number', 'user__username', 'slot__slot_id')
    readonly_fields = ('booked_at', 'end_time')
    list_per_page = 20

# You can also register UserProfile if you want to see it in the admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')