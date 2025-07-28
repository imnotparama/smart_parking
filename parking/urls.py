# parking/urls.py
from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    # --- Core User-Facing URLs ---
    path('', views.home, name='home'), # The root of the app is the main booking page
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('receipt/<int:booking_id>/', views.booking_receipt_view, name='booking_receipt'), # NEW
    
    # --- Analytics URLs ---
    path('my-analytics/', views.user_analytics_view, name='user_analytics'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # --- Auth & Static URLs ---
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('signup/', views.signup_view, name='signup_view'),
    path('help/', views.help_page, name='help_page'),
    
    # --- API URLs ---
    path('api/slots/', views.api_slots, name='api_slots'),
]