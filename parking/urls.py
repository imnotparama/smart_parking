# parking/urls.py
from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.home, name='book_slot'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('my-analytics/', views.user_analytics_view, name='user_analytics'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('help/', views.help_page, name='help_page'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('signup/', views.signup_view, name='signup_view'),
    path('api/slots/', views.api_slots, name='api_slots'),
]