# parking/admin.py

from django.contrib import admin
from .models import UserProfile, ParkingSlot, Booking

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ParkingSlot model.
    """
    list_display = ('__str__', 'status', 'floor', 'price', 'is_handicap', 'active_booking')
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
    search_fields = ('vehicle_number', 'user__username')
    readonly_fields = ('booked_at', 'end_time')
    list_per_page = 20

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')