# core/services/scheduler.py
import threading
import time
from datetime import datetime, timedelta
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class RainBankScheduler:
    """Background task scheduler for automated monitoring"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("RainBank scheduler started")
    
    def stop(self):
        """Stop the background scheduler"""
        self.running = False
        logger.info("RainBank scheduler stopped")
    
    def _run(self):
        """Main scheduler loop"""
        while self.running:
            try:
                now = timezone.now()
                
                # Daily tasks (run at 8 AM and 6 PM)
                if now.hour == 8 and now.minute == 0:
                    self._run_daily_tasks()
                    time.sleep(60)  # Sleep to avoid multiple runs
                
                # Hourly tasks
                if now.minute == 0:
                    self._run_hourly_tasks()
                
                # Check drought every 6 hours (at 00, 06, 12, 18)
                if now.hour in [0, 6, 12, 18] and now.minute == 0:
                    self._check_drought()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def _run_daily_tasks(self):
        """Run daily tasks (collect rainfall data)"""
        logger.info("Running daily tasks...")
        try:
            from core.services.satellite import RainfallDataCollector
            collector = RainfallDataCollector()
            result = collector.collect_all_farms()
            logger.info(f"Daily collection complete: {result}")
        except Exception as e:
            logger.error(f"Daily tasks error: {str(e)}")
    
    def _run_hourly_tasks(self):
        """Run hourly tasks (cleanup, monitoring)"""
        logger.debug("Running hourly tasks...")
        # Add any hourly tasks here
    
    def _check_drought(self):
        """Check for drought conditions"""
        logger.info("Checking drought conditions...")
        try:
            from core.services.satellite import DroughtDetector
            detector = DroughtDetector()
            results = detector.monitor_all_farms()
            logger.info(f"Drought check complete: {results}")
            
            # Log summary
            if results['drought_detected'] > 0:
                logger.warning(f"Drought detected on {results['drought_detected']} farms")
                logger.info(f"Created {results['payouts_created']} payouts")
                
        except Exception as e:
            logger.error(f"Drought check error: {str(e)}")

# Singleton instance
scheduler = RainBankScheduler()