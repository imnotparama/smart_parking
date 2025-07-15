# In parking/management/commands/seed_slots.py

import random
from django.core.management.base import BaseCommand
from parking.models import ParkingSlot

class Command(BaseCommand):
    help = 'Seeds the database with initial parking slots.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old parking slot data...")
        # To make the command re-runnable, we first delete all existing slots
        ParkingSlot.objects.all().delete()

        self.stdout.write("Creating new parking slots...")

        # --- Floor 1 ---
        # Section A: 18 slots
        for i in range(1, 19):
            ParkingSlot.objects.create(
                section='A',
                number=i,
                floor=1,
                price=random.choice([50.00, 60.00, 70.00]),
                is_handicap=(i % 5 == 0), # Every 5th slot is handicap
                is_ev_charging=(i % 3 == 0) # Every 3rd slot has EV charging
            )

        # Section B: 4 slots
        for i in [1, 2, 4, 10]: # Using the specific numbers from your original screenshot
             ParkingSlot.objects.create(
                section='B',
                number=i,
                floor=1,
                price=random.choice([50.00, 60.00]),
                is_handicap=(i == 2),
                is_ev_charging=(i == 4)
             )

        # --- Floor 2 ---
        # Section C: 10 slots
        for i in range(1, 11):
            ParkingSlot.objects.create(
                section='C',
                number=i,
                floor=2,
                price=80.00
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database with parking slots."))