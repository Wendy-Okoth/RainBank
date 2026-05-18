# core/management/commands/collect_rainfall.py
from django.core.management.base import BaseCommand
from core.services.satellite import RainfallDataCollector

class Command(BaseCommand):
    help = 'Collect daily rainfall data for all farms'
    
    def handle(self, *args, **options):
        self.stdout.write("Collecting rainfall data...")
        
        collector = RainfallDataCollector()
        results = collector.collect_all_farms()
        
        self.stdout.write(self.style.SUCCESS(f"\nResults:"))
        self.stdout.write(f"  Total farms: {results['total']}")
        self.stdout.write(f"  Data collected: {results['collected']}")
        self.stdout.write(f"  Errors: {results['errors']}")