from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.db.models import Count, Sum, F
from collections import defaultdict
from django.utils import timezone
from django.http import JsonResponse
from .models import ParkingSlot, Booking, User
from .forms import BookingForm, CustomLoginForm, CustomSignupForm
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ParkingSlot, Booking
from .forms import BookingForm


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

# parking/views.py
# parking/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import ParkingSlot, Booking
from .forms import BookingForm

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
            
            # --- EMAIL NOTIFICATION LOGIC (with try...except temporarily removed for debugging) ---
            
            # # try:
            subject = f'Your Parking Booking is Confirmed! - Slot {slot}'
            context = {
                'user': request.user,
                'booking': booking,
            }
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
            # # except Exception as e:
            # #     print(f"!!! CRITICAL: COULD NOT SEND BOOKING CONFIRMATION EMAIL: {e} !!!")
            # #     messages.warning(request, f"Your slot was booked successfully, but we could not send a confirmation email.")
            # --- END OF EMAIL LOGIC ---

            return redirect('my_bookings')
        else:
            messages.error(request, "Booking failed. Please check the details and try again.")
    
    return redirect('home')


@login_required
def my_bookings(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-parking_date', '-start_time')
    return render(request, 'parking/my_bookings.html', {'bookings': user_bookings})

@login_required
def analytics(request):
    # --- Key Metrics ---
    total_slots = ParkingSlot.objects.count()
    available_slots = ParkingSlot.objects.filter(is_available=True).count()
    occupied_slots = total_slots - available_slots
    
    total_bookings = Booking.objects.count()
    bookings_today = Booking.objects.filter(booked_at__date=timezone.now().date()).count()

    # Calculate total revenue
    total_revenue_agg = Booking.objects.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )
    total_revenue = total_revenue_agg['total'] or 0
    
    # Data for the "Bookings per slot" chart
    slot_stats = Booking.objects.values('slot__number').annotate(count=Count('id')).order_by('slot__number')

    context = {
        'total_slots': total_slots,
        'available_slots': available_slots,
        'occupied_slots': occupied_slots,
        'total_bookings': total_bookings,
        'bookings_today': bookings_today,
<<<<<<< HEAD
        'total_revenue': total_revenue, # You can add this to your template
        'slot_stats': slot_stats, # For the Chart.js
        'page_title': 'Analytics Dashboard'
    }
    return render(request, 'parking/analytics.html', context)
def help_page(request):
    return render(request, 'parking/help.html')

def api_slots(request):
    # This is a placeholder for your API logic.
    return JsonResponse({"status": "ok"})

# --- AUTH VIEWS ---

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
@login_required
def user_analytics_view(request):
    # Get analytics just for the current user
    user_bookings = Booking.objects.filter(user=request.user)
    total_bookings = user_bookings.count()
    
    total_spent_agg = user_bookings.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )
    total_spent = total_spent_agg['total'] or 0

    context = {
        'total_bookings': total_bookings,
        'total_spent': total_spent,
    }
    return render(request, 'parking/user_analytics.html', context)

# --- Analytics for Admins/Staff ---
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='home')
def admin_dashboard_view(request):
    total_users = User.objects.count()
    total_slots = ParkingSlot.objects.count()
    total_bookings = Booking.objects.count()
    
    # Calculate total revenue by multiplying the price of each booked slot by its duration
    total_revenue_agg = Booking.objects.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )
    total_revenue = total_revenue_agg['total'] or 0

    # --- Recent Activity ---
    # Get the 5 most recent bookings, with user and slot info pre-fetched for efficiency
    recent_bookings = Booking.objects.select_related('user', 'slot').order_by('-booked_at')[:5]
    
    # Get the 5 newest users who are not staff or superusers
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]

    context = {
        'total_users': total_users,
        'total_slots': total_slots,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'page_title': 'Admin Dashboard' # You can use this in your base.html
    }
    return render(request, 'parking/admin_dashboard.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.db.models import Count, Sum, F
from collections import defaultdict
from .models import ParkingSlot, Booking, User
from .forms import BookingForm, CustomLoginForm, CustomSignupForm # Make sure these forms are in forms.py

# ... your other views (home, login, signup, etc.) ...

# --- Analytics for Regular Users ---
@login_required
def user_analytics_view(request):
    user_bookings = Booking.objects.filter(user=request.user)
    total_bookings = user_bookings.count()
    
    total_spent_agg = user_bookings.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )
    total_spent = total_spent_agg['total'] or 0

    context = {
        'total_bookings': total_bookings,
        'total_spent': total_spent,
    }
    return render(request, 'parking/user_analytics.html', context)

# --- Analytics for Admins/Staff ---


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='home')
def admin_analytics_view(request):
    # --- Key Metrics ---
    total_users = User.objects.count()
    total_slots = ParkingSlot.objects.count()
    total_bookings = Booking.objects.count()
    
    total_revenue_agg = Booking.objects.aggregate(
        total=Sum(F('slot__price') * F('duration_hours'))
    )
    total_revenue = total_revenue_agg['total'] or 0

    # --- Recent & Top Activity ---
    recent_bookings = Booking.objects.select_related('user', 'slot').order_by('-booked_at')[:5]
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]
    
    # --- NEW: Top Booking Users ---
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
        'top_booking_users': top_booking_users, # Pass new data to template
        'page_title': 'Admin Dashboard'
    }
    return render(request, 'parking/admin_analytics.html', context)
@login_required
def cancel_booking(request, booking_id):
    # Find the booking that belongs to the current user, or return a 404 error
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # We only want to cancel if the request is a POST, to prevent accidental cancellations
    if request.method == 'POST':
        slot = booking.slot
        slot.is_available = True
        slot.save()
        booking.delete()
        messages.success(request, f"Booking for {slot} has been successfully cancelled.")
        return redirect('my_bookings')
    
    # If it's a GET request, just redirect to be safe
    return redirect('my_bookings')

=======
        'slot_stats': slot_stats,
    })
def help_page(request):
    return render(request, 'parking/help.html')
>>>>>>> 18187760977c2cd45c2e06343dbdba7c88205fea
