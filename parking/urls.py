# parking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Core pages
    path("", views.home, name="home"),
    path("book/", views.book_slot, name="book_slot"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("help/", views.help_page, name="help"),

    # Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),

    # User-specific analytics
    path("my-analytics/", views.user_analytics_view, name="user_analytics"),

    # Admin pages
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("admin-analytics/", views.admin_analytics_view, name="admin_analytics"),

    # API endpoint
    path("api/slots/", views.api_slots, name="api_slots"),
    
    # The old, broken URL has been removed from this file.
]