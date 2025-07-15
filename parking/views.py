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
from datetime import timedelta
from django.db.models.functions import TruncDay


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
        
    # ✅ MODIFIED: Get the active booking for the current user to highlight their slot
    user_active_booking = None
    if request.user.is_authenticated:
        user_active_booking = Booking.objects.filter(user=request.user, status='ACTIVE').first()

    form = BookingForm()
    context = {
        'sections': dict(sections),
        'all_floors': all_floors,
        'selected_floor': selected_floor,
        'form': form,
        'user_active_booking': user_active_booking,
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
            
            # ✅ MODIFIED: Check for 'ACTIVE' bookings specifically
            if Booking.objects.filter(user=request.user, status='ACTIVE').exists():
                messages.error(request, "You already have an active booking. Please cancel it before making a new one.")
                return redirect('my_bookings')

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

            try:
                send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [request.user.email], html_message=html_message, fail_silently=False)
            except Exception as e:
                # Log the error, but don't prevent the user from seeing the success message
                print(f"Email sending failed: {e}")
                messages.warning(request, "Booking successful, but confirmation email could not be sent.")

            messages.success(request, f"Slot {slot} booked successfully! A confirmation email has been sent.")
            return redirect('my_bookings')
        else:
            messages.error(request, "Booking failed. Please check the details and try again.")
    return redirect('home')


@login_required
def my_bookings(request):
    # ✅ MODIFIED: Fetch active bookings first, then past bookings
    active_bookings = Booking.objects.filter(user=request.user, status='ACTIVE').order_by('-booked_at')
    past_bookings = Booking.objects.filter(user=request.user).exclude(status='ACTIVE').order_by('-end_time')
    return render(request, 'parking/my_bookings.html', {'active_bookings': active_bookings, 'past_bookings': past_bookings})


@login_required
def cancel_booking(request, booking_id):
    # ✅ MODIFIED: Now sets status to CANCELLED instead of deleting the object
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='ACTIVE')
    if request.method == 'POST':
        slot = booking.slot
        slot.is_available = True
        slot.save()
        
        booking.status = Booking.BookingStatus.CANCELLED
        booking.save()
        
        messages.success(request, f"Booking for {slot} has been successfully cancelled.")
        return redirect('my_bookings')
    return redirect('my_bookings')


@login_required
def user_analytics_view(request):
    user_bookings = Booking.objects.filter(user=request.user)
    total_bookings = user_bookings.count()
    # ✅ MODIFIED: Calculates cost only from non-cancelled bookings
    total_spent = user_bookings.exclude(status='CANCELLED').aggregate(
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
    # This view can be merged with admin_analytics_view, but keeping it separate for clarity
    # If you have a separate template for it. The logic is duplicated in admin_analytics_view.
    total_users = User.objects.count()
    total_slots = ParkingSlot.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.exclude(status='CANCELLED').aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )['total'] or 0
    recent_bookings = Booking.objects.select_related('user', 'slot').order_by('-booked_at')[:5]
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]
    top_booking_users = User.objects.annotate(
        booking_count=Count('bookings')
    ).filter(booking_count__gt=0).order_by('-booking_count')[:5]

    context = {
        'total_users': total_users, 'total_slots': total_slots,
        'total_bookings': total_bookings, 'total_revenue': total_revenue,
        'recent_bookings': recent_bookings, 'recent_users': recent_users,
        'top_booking_users': top_booking_users, 'page_title': 'Admin Dashboard'
    }
    return render(request, 'parking/admin_dashboard.html', context)
    

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='home')
def admin_analytics_view(request):
    total_users = User.objects.count()
    total_slots = ParkingSlot.objects.count()
    total_bookings = Booking.objects.filter(status__in=['ACTIVE', 'COMPLETED']).count()
    total_revenue = Booking.objects.filter(status__in=['ACTIVE', 'COMPLETED']).aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )['total'] or 0
    recent_bookings = Booking.objects.select_related('user', 'slot').order_by('-booked_at')[:5]
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]
    top_booking_users = User.objects.annotate(
        booking_count=Count('bookings')
    ).filter(booking_count__gt=0).order_by('-booking_count')[:5]

    # ✅ NEW: Data for the 7-day revenue chart
    today = timezone.now().date()
    week_start = today - timedelta(days=6)
    revenue_by_day = Booking.objects.filter(
        status__in=['ACTIVE', 'COMPLETED'], parking_date__range=[week_start, today]
    ).annotate(day=TruncDay('parking_date')) \
     .values('day') \
     .annotate(daily_revenue=Sum(F('slot__price') * F('duration_hours'))) \
     .order_by('day')

    date_range = [week_start + timedelta(days=i) for i in range(7)]
    revenue_data = {d.strftime('%a'): 0 for d in date_range}
    for item in revenue_by_day:
        revenue_data[item['day'].strftime('%a')] = float(item['daily_revenue'])

    context = {
        'total_users': total_users, 'total_slots': total_slots,
        'total_bookings': total_bookings, 'total_revenue': total_revenue,
        'recent_bookings': recent_bookings, 'recent_users': recent_users,
        'top_booking_users': top_booking_users, 'page_title': 'Admin Analytics',
        'revenue_labels': list(revenue_data.keys()),
        'revenue_values': list(revenue_data.values()),
    }
    return render(request, 'parking/admin_analytics.html', context)


# ✅ NEW: Real-time API for slot status
def api_slots(request):
    floor = request.GET.get('floor', '1')
    slots = ParkingSlot.objects.filter(floor=floor).values('id', 'is_available')
    
    # Also check if the current user has an active booking on this floor
    user_booking_slot_id = None
    if request.user.is_authenticated:
        booking = Booking.objects.filter(user=request.user, status='ACTIVE', slot__floor=floor).first()
        if booking:
            user_booking_slot_id = booking.slot.id
            
    return JsonResponse({
        'slots': list(slots),
        'user_booking_slot_id': user_booking_slot_id
    })


def help_page(request):
    return render(request, 'parking/help.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
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