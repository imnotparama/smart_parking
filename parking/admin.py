<<<<<<< HEAD
# parking/admin.py
from django.contrib import admin
from .models import ParkingSlot, Booking, UserProfile

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'floor', 'section', 'number', 'price', 'is_available', 'is_handicap', 'is_ev_charging')
    list_filter = ('floor', 'section', 'is_available', 'is_handicap', 'is_ev_charging')
    search_fields = ('number', 'section')
    ordering = ('floor', 'section', 'number')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'slot', 'booked_at', 'vehicle_number', 'parking_date', 'start_time')
    list_filter = ('slot__floor', 'slot__section', 'booked_at')
    search_fields = ('user__username', 'slot__number', 'vehicle_number')
    readonly_fields = ('booked_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
=======
from django.contrib import admin
from .models import ParkingSlot

admin.site.register(ParkingSlot)
>>>>>>> 18187760977c2cd45c2e06343dbdba7c88205fea
