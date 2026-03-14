# parking/management/commands/seed_slots.py
from django.core.management.base import BaseCommand
from parking.models import ParkingSlot
import random

class Command(BaseCommand):
    help = 'Seeds the database with initial parking slots.'

    def handle(self, *args, **kwargs):
        if ParkingSlot.objects.exists():
            self.stdout.write('Parking slots already exist. Skipping seeding.')
            return
        self.stdout.write('Creating new parking slots...')
        
        floors = [1] # Let's start with one floor for simplicity
        sections = ['A', 'B']
        slots_per_section = 12

        total_slots = 0
        for floor in floors:
            for section in sections:
                for number in range(1, slots_per_section + 1):
                    slot_id_str = f"{section}{number}"
                    is_handicap = (section == 'B' and number % 4 == 0)
                    is_ev = (number % 3 == 0)
                    
                    slot = ParkingSlot(
                        floor=floor,
                        section=section,
                        number=number,
                        price=random.choice([50.00, 60.00, 70.00]),
                        is_handicap=is_handicap,
                        is_ev_charging=is_ev
                    )
                    slot.save()
                    total_slots += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {total_slots} parking slots on floor {floor}.'))