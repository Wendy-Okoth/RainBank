# core/management/commands/start_scheduler.py
from django.core.management.base import BaseCommand
from core.services.scheduler import scheduler

class Command(BaseCommand):
    help = 'Start the background task scheduler'
    
    def handle(self, *args, **options):
        self.stdout.write("Starting RainBank scheduler...")
        scheduler.start()
        self.stdout.write(self.style.SUCCESS("Scheduler running in background"))
        self.stdout.write("Press Ctrl+C to stop")
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("\nStopping scheduler...")
            scheduler.stop()
            self.stdout.write("Scheduler stopped")