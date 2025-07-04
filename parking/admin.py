from django.shortcuts import render
from .models import ParkingSlot

def home(request):
    slots = ParkingSlot.objects.all()
    return render(request, 'parking/home.html', {'slots': slots})

