# parking/views.py

# ==============================================================================
# == 1. IMPORTS
# ==============================================================================
# Standard Django Imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Sum, F, Q
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.functions import TruncDay

# Third-Party and Local App Imports
from collections import defaultdict
from datetime import datetime, timedelta
import pytz
from decimal import Decimal

from .models import ParkingSlot, Booking
from .forms import BookingForm, CustomLoginForm, CustomSignupForm
from .tasks import free_up_parking_slot

# Import the BackgroundTask model to manage scheduled tasks
from background_task.models import Task


# ==============================================================================
# == 2. CORE USER-FACING VIEWS
# ==============================================================================

@login_required
def home(request):
    """
    Handles both displaying the parking layout (GET) and processing a new
    booking (POST). This upgraded version includes dynamic pricing, advanced
    validation, real-time stats, and server-side filtering.
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            slot_id = form.cleaned_data.get('slot_id')
            parking_date = form.cleaned_data.get('parking_date')
            start_time = form.cleaned_data.get('start_time')
            duration = form.cleaned_data.get('duration')
            
            booking_start_datetime = ist.localize(datetime.combine(parking_date, start_time))

            if booking_start_datetime < now:
                messages.error(request, "You cannot book a time in the past.")
            
            elif Booking.objects.filter(user=request.user, status='ACTIVE').exists():
                messages.error(request, "You already have an active booking.")
                return redirect('parking:my_bookings')
            
            else:
                try:
                    slot = ParkingSlot.objects.get(id=slot_id, status='AVAILABLE')
                except ParkingSlot.DoesNotExist:
                    messages.error(request, "Sorry, this slot was just booked by someone else.")
                    return redirect('parking:home')

                base_price = slot.price
                final_price_per_hour = base_price
                is_peak_hour = 17 <= booking_start_datetime.hour < 21
                
                if is_peak_hour:
                    final_price_per_hour *= Decimal('1.20')
                    messages.info(request, f"Peak hour pricing is in effect (+20%).")
                
                booking = Booking.objects.create(
                    user=request.user,
                    slot=slot,
                    vehicle_number=form.cleaned_data.get('vehicle_number'),
                    parking_date=parking_date,
                    start_time=start_time,
                    duration_hours=duration,
                )

                slot.status = 'OCCUPIED'
                slot.active_booking = booking
                slot.save()

                free_up_parking_slot(booking.id, schedule=booking.end_time)
                
                total_cost = final_price_per_hour * duration
                messages.success(request, f"Slot {slot} booked successfully! Total: ₹{total_cost:.2f}")
                return redirect('parking:my_bookings')
    else:
        form = BookingForm()

    all_slots_query = ParkingSlot.objects.all()
    filter_handicap = request.GET.get('is_handicap') == 'on'
    filter_ev = request.GET.get('is_ev_charging') == 'on'
    if filter_handicap:
        all_slots_query = all_slots_query.filter(is_handicap=True)
    if filter_ev:
        all_slots_query = all_slots_query.filter(is_ev_charging=True)

    total_slots = all_slots_query.count()
    available_slots = all_slots_query.filter(status='AVAILABLE').count()
    occupancy_percentage = int((total_slots - available_slots) / total_slots * 100) if total_slots > 0 else 0
    
    current_hour = now.hour
    if 5 <= current_hour < 12:
        greeting = f"Good morning, {request.user.username}!"
    elif 12 <= current_hour < 17:
        greeting = f"Good afternoon, {request.user.username}!"
    else:
        greeting = f"Good evening, {request.user.username}!"

    sections = defaultdict(list)
    for slot in all_slots_query.order_by('floor', 'section', 'number'):
        sections[f"Floor {slot.floor} - Section {slot.section}"].append(slot)

    context = {
        'sections': dict(sections),
        'form': form,
        'stats': { 'total': total_slots, 'available': available_slots, 'occupancy': occupancy_percentage, },
        'greeting': greeting,
        'filters': { 'handicap': filter_handicap, 'ev': filter_ev, }
    }
    return render(request, 'parking/home.html', context)


@login_required
def my_bookings(request):
    active_bookings = Booking.objects.filter(user=request.user, status='ACTIVE').order_by('-booked_at')
    past_bookings = Booking.objects.filter(user=request.user).exclude(status='ACTIVE').order_by('-end_time')
    context = { 'active_bookings': active_bookings, 'past_bookings': past_bookings }
    return render(request, 'parking/my_bookings.html', context)


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='ACTIVE')
    if request.method == 'POST':
        slot = booking.slot
        slot.status = 'AVAILABLE'
        slot.active_booking = None
        slot.save()
        booking.status = Booking.BookingStatus.CANCELLED
        booking.save()
        
        try:
            task_params = f'[{booking.id}]'
            task = Task.objects.get(task_name='parking.tasks.free_up_parking_slot', task_params__contains=task_params)
            task.delete()
        except Task.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error deleting task: {e}")
        
        messages.success(request, f"Booking for {slot} has been successfully cancelled.")
        return redirect('parking:my_bookings')
    return redirect('parking:my_bookings')


# ==============================================================================
# == 3. ANALYTICS & ADMIN VIEWS
# ==============================================================================

@login_required
def user_analytics_view(request):
    """
    Displays personal analytics for the logged-in user, including
    data prepared for Chart.js visualizations.
    """
    user_bookings = Booking.objects.filter(user=request.user).exclude(status='CANCELLED')
    
    total_bookings = user_bookings.count()
    total_spent = user_bookings.aggregate(total=Sum(F('slot__price') * F('duration_hours')))['total'] or 0

    spending_by_section = user_bookings.values('slot__section').annotate(total=Sum(F('slot__price') * F('duration_hours'))).order_by('slot__section')
    section_labels = [item['slot__section'] for item in spending_by_section]
    section_spending = [float(item['total']) for item in spending_by_section]

    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # --- THE FIX IS HERE ---
    # Annotate bookings with their weekday, excluding any potential null dates
    bookings_by_day = user_bookings.filter(booked_at__isnull=False).annotate(
        weekday=TruncDay('booked_at__date')
    ).values('weekday').annotate(
        count=Count('id')
    ).order_by('weekday')

    daily_counts = {day: 0 for day in days_of_week}
    
    for item in bookings_by_day:
        # Add a check to ensure 'weekday' is not None before processing
        if item['weekday']:
            day_index = item['weekday'].weekday() # 0=Mon, 1=Tue, ...
            day_name = days_of_week[day_index]
            daily_counts[day_name] = item['count']
    # --- END OF FIX ---

    context = {
        'total_bookings': total_bookings,
        'total_spent': total_spent,
        'section_chart_labels': section_labels,
        'section_chart_data': section_spending,
        'daily_chart_labels': list(daily_counts.keys()),
        'daily_chart_data': list(daily_counts.values()),
    }
    return render(request, 'parking/user_analytics.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='parking:home')
def admin_dashboard_view(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_slots = ParkingSlot.objects.count()
    active_bookings_count = Booking.objects.filter(status='ACTIVE').count()
    total_revenue = Booking.objects.exclude(status='CANCELLED').aggregate(total=Sum(F('slot__price') * F('duration_hours')))['total'] or 0
    recent_bookings = Booking.objects.select_related('user', 'slot').order_by('-booked_at')[:5]
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]
    today = timezone.now().date()
    week_start = today - timedelta(days=6)
    revenue_by_day = Booking.objects.filter(
        status__in=['ACTIVE', 'COMPLETED'],
        booked_at__date__range=[week_start, today]
    ).annotate(day=TruncDay('booked_at__date')).values('day').annotate(daily_revenue=Sum(F('slot__price') * F('duration_hours'))).order_by('day')
    date_range = [week_start + timedelta(days=i) for i in range(7)]
    revenue_data = {d.strftime('%a'): 0 for d in date_range}
    for item in revenue_by_day:
        if item['day']:
            revenue_data[item['day'].strftime('%a')] = float(item['daily_revenue'])
    context = {
        'total_users': total_users, 'total_slots': total_slots, 'active_bookings_count': active_bookings_count,
        'total_revenue': total_revenue, 'recent_bookings': recent_bookings, 'recent_users': recent_users,
        'chart_labels': list(revenue_data.keys()), 'chart_data': list(revenue_data.values()),
    }
    return render(request, 'parking/admin_dashboard.html', context)

# ==============================================================================
# == 4. AUTHENTICATION & STATIC PAGES
# ==============================================================================
def help_page(request): return render(request, 'parking/help.html')
def login_view(request):
    if request.user.is_authenticated: return redirect('parking:home')
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                auth_login(request, user)
                next_url = request.GET.get('next', 'parking:home')
                return redirect(next_url)
            else: messages.error(request, "Invalid username or password.")
    else: form = CustomLoginForm()
    return render(request, 'parking/login.html', {'form': form})
def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('parking:login_view')
def signup_view(request):
    if request.user.is_authenticated: return redirect('parking:home')
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created successfully! Welcome.")
            return redirect('parking:home')
    else: form = CustomSignupForm()
    return render(request, 'parking/signup.html', {'form': form})

# ==============================================================================
# == 5. API ENDPOINTS
# ==============================================================================
def api_slots(request):
    slots_data = ParkingSlot.objects.all().values('id', 'status', 'active_booking__user_id')
    return JsonResponse({'slots': list(slots_data)})