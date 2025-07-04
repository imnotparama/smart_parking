from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from .models import ParkingSlot, Booking

def home(request):
    slots = ParkingSlot.objects.all().order_by('number')
    my_booking = None
    available_count = slots.filter(is_available=True).count()
    occupied_count = slots.filter(is_available=False).count()
    parking_cost_per_minute = 2

    minutes_parked = total_cost = None
    if request.user.is_authenticated:
        my_booking = Booking.objects.filter(user=request.user).first()
        if my_booking:
            now = timezone.now()
            minutes_parked = int((now - my_booking.booked_at).total_seconds() // 60)
            total_cost = minutes_parked * parking_cost_per_minute

    return render(request, 'parking/home.html', {
        'slots': slots,
        'my_booking': my_booking,
        'available_count': available_count,
        'occupied_count': occupied_count,
        'minutes_parked': minutes_parked,
        'parking_cost_per_minute': parking_cost_per_minute,
        'total_cost': total_cost,
    })

@login_required(login_url='login')
def book_slot(request, slot_id):
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    existing_booking = Booking.objects.filter(user=request.user, slot=slot).first()
    if existing_booking:
        messages.warning(request, f"You have already booked Slot {slot.number}.")
        return redirect('home')
    if slot.is_available:
        slot.is_available = False
        slot.save()
        Booking.objects.create(slot=slot, user=request.user)
        messages.success(request, f"✅ Slot {slot.number} booked successfully!")
    else:
        messages.warning(request, f"❌ Slot {slot.number} is already occupied.")
    return redirect('home')

@login_required(login_url='login')
def cancel_booking(request, slot_id):
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    booking = Booking.objects.filter(slot=slot, user=request.user).first()
    if booking:
        booking.delete()
        slot.is_available = True
        slot.save()
        messages.success(request, f"🚫 Booking for Slot {slot.number} canceled.")
    else:
        messages.warning(request, "You are not allowed to cancel this booking.")
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! 🎉")
            return redirect('home')
        else:
            messages.error(request, "Something went wrong. Please try again.")
    else:
        form = UserCreationForm()
    return render(request, 'parking/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'parking/login.html', {'form': form})

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required(login_url='login')
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('slot').order_by('-booked_at')
    return render(request, 'parking/my_bookings.html', {'bookings': bookings})

@login_required(login_url='login')
def analytics(request):
    slots = ParkingSlot.objects.all()
    total_slots = slots.count()
    available_slots = slots.filter(is_available=True).count()
    occupied_slots = slots.filter(is_available=False).count()
    total_bookings = Booking.objects.count()
    today = timezone.now().date()
    bookings_today = Booking.objects.filter(booked_at__date=today).count()
    slot_stats = (
        Booking.objects.values('slot__number')
        .annotate(count=Count('id'))
        .order_by('slot__number')
    )
    return render(request, 'parking/analytics.html', {
        'total_slots': total_slots,
        'available_slots': available_slots,
        'occupied_slots': occupied_slots,
        'total_bookings': total_bookings,
        'bookings_today': bookings_today,
        'slot_stats': slot_stats,
    })