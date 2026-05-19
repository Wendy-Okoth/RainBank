# core/management/commands/check_drought.py
from django.core.management.base import BaseCommand
from core.services.satellite import DroughtDetector
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check all farms for drought conditions and create payouts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--farm-id',
            type=int,
            help='Check a specific farm by ID',
        )
    
    def handle(self, *args, **options):
        detector = DroughtDetector()
        
        if options['farm_id']:
            from core.models import Farm
            try:
                farm = Farm.objects.get(id=options['farm_id'])
                self.stdout.write(f"Checking farm: {farm}")
                result = detector.check_drought_for_farm(farm)
                self.stdout.write(self.style.SUCCESS(f"Result: {result}"))
            except Farm.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Farm {options['farm_id']} not found"))
        else:
            self.stdout.write("Checking all active farms for drought...")
            results = detector.monitor_all_farms()
            
            self.stdout.write(self.style.SUCCESS(f"\nResults:"))
            self.stdout.write(f"  Farms checked: {results['checked']}")
            self.stdout.write(f"  Drought detected: {results['drought_detected']}")
            self.stdout.write(f"  Payouts created: {results['payouts_created']}")
            self.stdout.write(f"  Errors: {results['errors']}")
            
            if results['details']:
                self.stdout.write("\nDetails:")
                for detail in results['details'][:10]:
                    self.stdout.write(f"  {detail}")