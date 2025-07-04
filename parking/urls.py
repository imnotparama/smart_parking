from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('cancel/<int:slot_id>/', views.cancel_booking, name='cancel_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('analytics/', views.analytics, name='analytics'),  # <--- THIS LINE IS REQUIRED!
]