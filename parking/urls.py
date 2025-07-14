# parking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("book/", views.book_slot, name="book_slot"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),

    # Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),

    # Extras
    path("analytics/", views.analytics, name="analytics"),
    path("help/", views.help_page, name="help"),

    # Admin
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("admin-analytics/", views.admin_analytics_view, name="admin_analytics"),

    # User analytics
    path("my-analytics/", views.user_analytics_view, name="user_analytics"),

    # API
    path("api/slots/", views.api_slots, name="api_slots"),
]
