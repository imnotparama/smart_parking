from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Sum, F
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from collections import defaultdict

from .models import ParkingSlot, Booking, User
from .forms import BookingForm, CustomLoginForm, CustomSignupForm


def home(request):
    all_floors = list(ParkingSlot.objects.values_list('floor', flat=True).distinct().order_by('floor'))
    selected_floor_str = request.GET.get('floor', all_floors[0] if all_floors else 1)

    try:
        selected_floor = int(selected_floor_str)
    except (ValueError, TypeError):
        selected_floor = all_floors[0] if all_floors else 1

    slots = ParkingSlot.objects.filter(floor=selected_floor)
    sections = defaultdict(list)
    for slot in slots:
        sections[slot.section].append(slot)

    form = BookingForm()
    context = {
        'sections': dict(sections),
        'all_floors': all_floors,
        'selected_floor': selected_floor,
        'form': form,
    }
    return render(request, 'parking/home.html', context)


@login_required
def book_slot(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            slot_id = form.cleaned_data.get('slot_id')
            if not slot_id:
                messages.error(request, "Please select a parking slot before booking.")
                return redirect('home')

            try:
                slot = ParkingSlot.objects.get(id=slot_id, is_available=True)
            except ParkingSlot.DoesNotExist:
                messages.error(request, "This slot is no longer available or has already been booked.")
                return redirect('home')

            if Booking.objects.filter(user=request.user).exists():
                messages.error(request, "You already have an active booking. Please cancel it before making a new one.")
                return redirect('my_bookings')

            # Ensure all required fields are passed
            booking = Booking.objects.create(
                user=request.user,
                slot=slot,
                vehicle_number=form.cleaned_data['vehicle_number'],
                parking_date=form.cleaned_data['parking_date'],
                start_time=form.cleaned_data['start_time'],
                duration_hours=form.cleaned_data['duration']
            )
            slot.is_available = False
            slot.save()

            subject = f'Your Parking Booking is Confirmed! - Slot {slot}'
            context = {'user': request.user, 'booking': booking}
            html_message = render_to_string('parking/emails/booking_confirmation.html', context)
            plain_message = f"Hi {request.user.username},\n\nYour booking for Slot {slot} is confirmed. Thank you!"

            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                html_message=html_message,
                fail_silently=False
            )

            messages.success(request, f"Slot {slot} booked successfully! A confirmation email has been sent.")
            return redirect('my_bookings')
        else:
            messages.error(request, "Booking failed. Please check the details and try again.")
    return redirect('home')


@login_required
def my_bookings(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-parking_date', '-start_time')
    return render(request, 'parking/my_bookings.html', {'bookings': user_bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        slot = booking.slot
        slot.is_available = True
        slot.save()
        booking.delete()
        messages.success(request, f"Booking for {slot} has been successfully cancelled.")
        return redirect('my_bookings')
    return redirect('my_bookings')


@login_required
def analytics(request):
    total_slots = ParkingSlot.objects.count()
    available_slots = ParkingSlot.objects.filter(is_available=True).count()
    occupied_slots = total_slots - available_slots
    total_bookings = Booking.objects.count()
    bookings_today = Booking.objects.filter(booked_at__date=timezone.now().date()).count()
    total_revenue = Booking.objects.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )['total'] or 0
    slot_stats = Booking.objects.values('slot__number').annotate(count=Count('id')).order_by('slot__number')

    context = {
        'total_slots': total_slots,
        'available_slots': available_slots,
        'occupied_slots': occupied_slots,
        'total_bookings': total_bookings,
        'bookings_today': bookings_today,
        'total_revenue': total_revenue,
        'slot_stats': slot_stats,
        'page_title': 'Analytics Dashboard'
    }
    return render(request, 'parking/analytics.html', context)


@login_required
def user_analytics_view(request):
    user_bookings = Booking.objects.filter(user=request.user)
    total_bookings = user_bookings.count()
    total_spent = user_bookings.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )['total'] or 0

    context = {
        'total_bookings': total_bookings,
        'total_spent': total_spent,
    }
    return render(request, 'parking/user_analytics.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='home')
def admin_dashboard_view(request):
    total_users = User.objects.count()
    total_slots = ParkingSlot.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )['total'] or 0
    recent_bookings = Booking.objects.select_related('user', 'slot').order_by('-booked_at')[:5]
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]
    top_booking_users = User.objects.annotate(
        booking_count=Count('booking')
    ).filter(booking_count__gt=0).order_by('-booking_count')[:5]

    context = {
        'total_users': total_users,
        'total_slots': total_slots,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'top_booking_users': top_booking_users,
        'page_title': 'Admin Dashboard'
    }
    return render(request, 'parking/admin_dashboard.html', context)


def help_page(request):
    return render(request, 'parking/help.html')


def api_slots(request):
    return JsonResponse({"status": "ok"})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'parking/login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = CustomSignupForm()
    return render(request, 'parking/signup.html', {'form': form})


# Separate admin view for standalone admin analytics template (optional use)
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_analytics_view(request):
    total_users = User.objects.count()
    total_slots = ParkingSlot.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )['total'] or 0
    recent_bookings = Booking.objects.select_related('user', 'slot').order_by('-booked_at')[:5]
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]
    top_booking_users = User.objects.annotate(
        booking_count=Count('booking')
    ).filter(booking_count__gt=0).order_by('-booking_count')[:5]

    context = {
        'total_users': total_users,
        'total_slots': total_slots,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'top_booking_users': top_booking_users,
        'page_title': 'Admin Dashboard'
    }
    return render(request, 'admin/analytics.html', context)
