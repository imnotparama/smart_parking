from django.contrib import admin
from .models import ParkingSlot, Booking, UserProfile

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('number', 'floor', 'section', 'is_available', 'price')
    list_filter = ('floor', 'section', 'is_available')
    search_fields = ('number',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'slot', 'parking_date', 'start_time', 'duration_hours', 'booked_at')
    list_filter = ('parking_date',)
    search_fields = ('user__username', 'slot__number')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
