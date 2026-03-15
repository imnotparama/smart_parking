# parking/views.py

# ==============================================================================
# == 1. IMPORTS
# ==============================================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from datetime import datetime, timedelta
import pytz
from decimal import Decimal

from .models import ParkingSlot, Booking, UserProfile
from .forms import BookingForm, CustomLoginForm, CustomSignupForm
from .tasks import free_up_parking_slot
from background_task.models import Task

# ==============================================================================
# == 2. HELPER FUNCTIONS
# ==============================================================================

def is_admin(user):
    """A helper function to check if a user is a staff member."""
    return user.is_staff

# ==============================================================================
# == 3. CORE USER-FACING VIEWS
# ==============================================================================

@login_required
def home(request):
    """
    Handles both displaying the parking layout (GET) and processing a new
    booking (POST). This final version correctly handles form validation, sends
    email confirmations, and includes robust server-side validation.
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            slot_id = form.cleaned_data['slot_id']
            parking_date = form.cleaned_data['parking_date']
            start_time = form.cleaned_data['start_time']
            
            booking_start_datetime = ist.localize(datetime.combine(parking_date, start_time))
            if booking_start_datetime < now:
                messages.error(request, "Validation failed: You cannot book a time in the past.")
            
            elif Booking.objects.filter(user=request.user, status='ACTIVE').exists():
                messages.error(request, "You already have an active booking. Please cancel it before making a new one.")
                return redirect('parking:my_bookings')

            else:
                try:
                    slot = ParkingSlot.objects.get(id=slot_id, status='AVAILABLE')
                except ParkingSlot.DoesNotExist:
                    messages.error(request, "Sorry, this slot was just booked by someone else.")
                    return redirect('parking:home')

                booking = form.save(commit=False)
                booking.user = request.user
                booking.slot = slot
                booking.save()

                slot.status = 'OCCUPIED'
                slot.active_booking = booking
                slot.save()

                free_up_parking_slot(booking.id, schedule=booking.end_time)

                # --- Send Confirmation Email ---
                try:
                    subject = f"Your Parking Booking Confirmation (ID: {booking.booking_id})"
                    html_message = render_to_string('parking/emails/booking_confirmation.html', {'booking': booking})
                    plain_message = f"Your booking for slot {booking.slot} is confirmed."
                    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [request.user.email], html_message=html_message)
                    messages.success(request, f"Slot {slot} booked successfully! A confirmation has been sent.")
                except Exception as e:
                    print(f"EMAIL SENDING FAILED for booking {booking.id}: {e}")
                    messages.warning(request, f"Slot {slot} booked successfully, but we couldn't send a confirmation email.")

                return redirect('parking:my_bookings')
        else:
            messages.error(request, "Please correct the errors shown on the form.")
    else:
        form = BookingForm()

    all_slots_query = ParkingSlot.objects.all()
    total_slots = all_slots_query.count()
    available_slots = all_slots_query.filter(status='AVAILABLE').count()
    occupancy_percentage = int((total_slots - available_slots) / total_slots * 100) if total_slots > 0 else 0
    
    current_hour = now.hour
    greeting = "Good evening"
    if 5 <= current_hour < 12: greeting = "Good morning"
    elif 12 <= current_hour < 17: greeting = "Good afternoon"
    greeting += f", {request.user.username}!"

    sections = defaultdict(list)
    for slot in all_slots_query.order_by('floor', 'section', 'number'):
        sections[f"Floor {slot.floor} - Section {slot.section}"].append(slot)

    context = {
        'form': form,
        'sections': dict(sections),
        'stats': { 'total': total_slots, 'available': available_slots, 'occupancy': occupancy_percentage },
        'greeting': greeting,
    }
    return render(request, 'parking/home.html', context)

@login_required
def my_bookings(request):
    """Displays the user's active and past bookings."""
    active_bookings = Booking.objects.filter(user=request.user, status='ACTIVE').order_by('-booked_at')
    past_bookings = Booking.objects.filter(user=request.user).exclude(status='ACTIVE').order_by('-end_time')[:10]
    context = {'active_bookings': active_bookings, 'past_bookings': past_bookings}
    return render(request, 'parking/my_bookings.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Handles the cancellation of an active booking."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='ACTIVE')
    if request.method == 'POST':
        slot = booking.slot
        slot.status = 'AVAILABLE'
        slot.active_booking = None
        slot.save()
        booking.status = Booking.BookingStatus.CANCELLED
        booking.save()
        try:
            task = Task.objects.get(task_name='parking.tasks.free_up_parking_slot', task_params__contains=f'[{booking.id}]')
            task.delete()
        except Task.DoesNotExist:
            pass
        messages.success(request, f"Booking for {slot} has been successfully cancelled.")
    return redirect('parking:my_bookings')

@login_required
def booking_receipt_view(request, booking_id):
    """Displays a clean, printable receipt for a specific booking."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'parking/booking_receipt.html', {'booking': booking})

# ==============================================================================
# == 4. ANALYTICS & ADMIN VIEWS
# ==============================================================================

@login_required
def user_analytics_view(request):
    """Displays personal analytics for the logged-in user."""
    user_bookings = Booking.objects.filter(user=request.user).exclude(status='CANCELLED')
    total_bookings = user_bookings.count()
    total_spent = user_bookings.aggregate(total=Sum('total_cost'))['total'] or Decimal('0.00')
    context = {'total_bookings': total_bookings, 'total_spent': total_spent}
    return render(request, 'parking/user_analytics.html', context)

@login_required
@user_passes_test(is_admin, login_url='parking:home')
def admin_dashboard_view(request):
    """Displays the main dashboard for staff users."""
    total_users = User.objects.filter(is_staff=False).count()
    total_slots = ParkingSlot.objects.count()
    active_bookings_count = Booking.objects.filter(status='ACTIVE').count()
    total_revenue = Booking.objects.exclude(status='CANCELLED').aggregate(total=Sum('total_cost'))['total'] or 0
    recent_bookings = Booking.objects.select_related('user', 'slot').order_by('-booked_at')[:5]
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]
    context = {
        'total_users': total_users, 'total_slots': total_slots,
        'active_bookings_count': active_bookings_count, 'total_revenue': total_revenue,
        'recent_bookings': recent_bookings, 'recent_users': recent_users,
    }
    return render(request, 'parking/admin_dashboard.html', context)

# ==============================================================================
# == 5. AUTHENTICATION & STATIC PAGES
# ==============================================================================

def login_view(request):
    """Handles user login."""
    if request.user.is_authenticated:
        return redirect('parking:home')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('parking:home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'parking/login.html', {'form': form})

def signup_view(request):
    """Handles new user registration."""
    if request.user.is_authenticated:
        return redirect('parking:home')
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('parking:home')
    else:
        form = CustomSignupForm()
    return render(request, 'parking/signup.html', {'form': form})

def logout_view(request):
    """Logs the user out."""
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('parking:login_view')

def help_page(request):
    """Renders the static help page."""
    return render(request, 'parking/help.html')

# ==============================================================================
# == 6. API ENDPOINTS
# ==============================================================================

def api_slots(request):
    """A simple API endpoint to provide real-time slot status."""
    slots_data = ParkingSlot.objects.all().values('id', 'status')
    return JsonResponse(list(slots_data), safe=False)


# ==============================================================================
# == 7. CRON JOB ENDPOINT (replaces django-background-tasks on Vercel)
# ==============================================================================

@csrf_exempt
def process_tasks_cron(request):
    """
    Vercel cron endpoint — called every 10 minutes via vercel.json.
    Finds all ACTIVE bookings whose end_time has passed and releases the slot.
    Protected by a CRON_SECRET header to prevent abuse.
    """
    # Security check: only allow requests with the correct secret
    cron_secret = settings.CRON_SECRET
    if cron_secret:
        provided = request.headers.get('Authorization', '')
        if provided != f'Bearer {cron_secret}':
            return JsonResponse({'error': 'Unauthorized'}, status=401)

    now = timezone.now()
    expired_bookings = Booking.objects.filter(
        status=Booking.BookingStatus.ACTIVE,
        end_time__lte=now
    ).select_related('slot')

    released = []
    for booking in expired_bookings:
        slot = booking.slot
        slot.status = ParkingSlot.SlotStatus.AVAILABLE
        slot.active_booking = None
        slot.save()

        booking.status = Booking.BookingStatus.COMPLETED
        booking.save()
        released.append(booking.booking_id)

    return JsonResponse({
        'status': 'ok',
        'released_count': len(released),
        'released_booking_ids': released,
        'processed_at': now.isoformat(),
    })

# ==============================================================================
# == 8. REMOTE DB SETUP ENDPOINT (for initial Vercel setup)
# ==============================================================================

@csrf_exempt
def setup_db_view(request):
    """
    Runs migrations and seeds the database remotely. 
    Protected by the CRON_SECRET header or GET parameter.
    """
    cron_secret = settings.CRON_SECRET
    provided = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not provided:
        provided = request.GET.get('secret', '')
        
    if not cron_secret or provided != cron_secret:
        return JsonResponse({'error': 'Unauthorized setup attempt'}, status=401)
        
    from django.core.management import call_command
    from django.contrib.auth import get_user_model
    import traceback
    
    try:
        # Run migrations
        call_command('migrate', interactive=False)
        
        # Seed slots
        call_command('seed_slots')
        
        # Create superuser if it doesn't exist
        User = get_user_model()
        admin_created = False
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            admin_created = True
            
        return JsonResponse({
            'status': 'success',
            'message': 'Database migrated and seeded successfully!',
            'admin_created': admin_created
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
