# core/services/satellite.py
import requests
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.utils import timezone
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class NASAPowerAPI:
    """NASA POWER API client for rainfall data"""
    
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    def __init__(self):
        self.timeout = 30  # seconds
    
    def get_daily_rainfall(self, latitude, longitude, start_date, end_date):
        """
        Fetch daily rainfall data from NASA POWER
        
        Args:
            latitude: Decimal latitude (-90 to 90)
            longitude: Decimal longitude (-180 to 180)
            start_date: datetime.date object
            end_date: datetime.date object
        
        Returns:
            dict: {date: rainfall_mm} or None if error
        """
        # Check cache first (cache for 6 hours)
        cache_key = f"nasa_rainfall_{latitude}_{longitude}_{start_date}_{end_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached rainfall data for {latitude}, {longitude}")
            return cached_data
        
        try:
            params = {
                'parameters': 'PRECTOTCORR',  # Precipitation corrected
                'community': 'AG',
                'format': 'JSON',
                'start': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d'),
                'latitude': float(latitude),
                'longitude': float(longitude),
                'user': 'rainbank'
            }
            
            logger.info(f"Fetching rainfall data for {latitude}, {longitude} from {start_date} to {end_date}")
            
            response = requests.get(
                self.BASE_URL, 
                params=params, 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                rainfall_data = {}
                
                # Extract rainfall values (mm per day)
                if 'properties' in data and 'parameter' in data['properties']:
                    rainfall_dict = data['properties']['parameter'].get('PRECTOTCORR', {})
                    
                    for date_str, value in rainfall_dict.items():
                        # Convert date string to date object
                        try:
                            rain_date = datetime.strptime(date_str, '%Y%m%d').date()
                            # Filter out invalid NASA values (-999 means no data)
                            if value >= 0:
                                rainfall_data[rain_date] = float(value)
                            else:
                                rainfall_data[rain_date] = 0.0  # Treat missing as 0 rain
                        except:
                            continue
                
                # Cache the result for 6 hours
                cache.set(cache_key, rainfall_data, 3600 * 6)
                logger.info(f"Successfully fetched {len(rainfall_data)} days of rainfall data")
                return rainfall_data
            else:
                logger.error(f"NASA API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"NASA API timeout for {latitude}, {longitude}")
            return None
        except Exception as e:
            logger.error(f"Error fetching NASA data: {str(e)}")
            return None
    
    def get_historical_average(self, latitude, longitude, target_date, years=30):
        """
        Get historical average rainfall for a specific date
        
        Args:
            latitude: Decimal latitude
            longitude: Decimal longitude
            target_date: datetime.date object
            years: Number of years for average (default 30)
        
        Returns:
            float: Average rainfall in mm
        """
        try:
            # Calculate date range (same month/day over Y years)
            end_date = target_date
            start_date = target_date.replace(year=target_date.year - years)
            
            # Fetch historical data
            rainfall_data = self.get_daily_rainfall(latitude, longitude, start_date, end_date)
            
            if not rainfall_data:
                return None
            
            # Collect rainfall for same month/day across years
            historical_values = []
            for year in range(target_date.year - years, target_date.year + 1):
                try:
                    check_date = target_date.replace(year=year)
                    if check_date in rainfall_data:
                        historical_values.append(rainfall_data[check_date])
                except:
                    continue
            
            if historical_values:
                return sum(historical_values) / len(historical_values)
            return 5.0  # Default fallback: 5mm per day
            
        except Exception as e:
            logger.error(f"Error calculating historical average: {str(e)}")
            return 5.0  # Default fallback


class DroughtDetector:
    """Detect drought conditions using satellite data"""
    
    def __init__(self):
        self.nasa_api = NASAPowerAPI()
    
    def check_drought_for_farm(self, farm, days_to_check=10, threshold_percent=70):
        """
        Check if a farm is experiencing drought conditions
        
        Args:
            farm: Farm model instance
            days_to_check: Number of consecutive days to check (default 10)
            threshold_percent: Percentage below average to trigger (default 70%)
        
        Returns:
            dict: {
                'is_drought': bool,
                'consecutive_dry_days': int,
                'rainfall_actual': float,
                'rainfall_average': float,
                'details': str
            }
        """
        if not farm.latitude or not farm.longitude:
            logger.warning(f"Farm {farm.id} missing coordinates")
            return {
                'is_drought': False,
                'consecutive_dry_days': 0,
                'rainfall_actual': 0,
                'rainfall_average': 0,
                'details': 'Farm coordinates missing'
            }
        
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days_to_check + 30)  # Extra for average
            
            # Fetch recent rainfall data
            rainfall_data = self.nasa_api.get_daily_rainfall(
                farm.latitude, 
                farm.longitude, 
                start_date, 
                end_date
            )
            
            if not rainfall_data:
                return {
                    'is_drought': False,
                    'consecutive_dry_days': 0,
                    'rainfall_actual': 0,
                    'rainfall_average': 0,
                    'details': 'Failed to fetch rainfall data'
                }
            
            # Get last N days, filtering out invalid values
            recent_days = []
            for i in range(days_to_check):
                check_date = end_date - timedelta(days=i)
                if check_date in rainfall_data:
                    rain_value = rainfall_data[check_date]
                    # Ensure no negative values
                    if rain_value < 0:
                        rain_value = 0
                    recent_days.append(rain_value)
                else:
                    recent_days.append(0)  # Missing data treated as 0
            
            # Calculate average using recent 30-day period (simpler and more reliable)
            # Get average from days 30-45 days ago (to avoid current drought period)
            historical_days = []
            for i in range(30, 45):  # Look at days 30-45 days ago
                check_date = end_date - timedelta(days=i)
                if check_date in rainfall_data:
                    rain_value = rainfall_data[check_date]
                    if rain_value >= 0:
                        historical_days.append(rain_value)
            
            if historical_days:
                avg_daily_rainfall = sum(historical_days) / len(historical_days)
            else:
                # Fallback: use a reasonable default for semi-arid regions (like Machakos)
                avg_daily_rainfall = 3.0  # 3mm per day average
            
            # Calculate threshold
            threshold = avg_daily_rainfall * (threshold_percent / 100)
            
            # Count consecutive dry days (below threshold)
            consecutive_dry = 0
            for rain in recent_days:
                if rain < threshold:
                    consecutive_dry += 1
                else:
                    break  # Break on first wet day
            
            is_drought = consecutive_dry >= days_to_check
            
            return {
                'is_drought': is_drought,
                'consecutive_dry_days': consecutive_dry,
                'rainfall_actual': sum(recent_days),
                'rainfall_average': avg_daily_rainfall * days_to_check,
                'details': f"{consecutive_dry} consecutive dry days out of {days_to_check} (threshold: {threshold:.1f}mm/day)",
                'daily_rainfall': recent_days,
                'threshold': threshold,
                'avg_daily_rainfall': avg_daily_rainfall
            }
            
        except Exception as e:
            logger.error(f"Error checking drought for farm {farm.id}: {str(e)}")
            return {
                'is_drought': False,
                'consecutive_dry_days': 0,
                'rainfall_actual': 0,
                'rainfall_average': 0,
                'details': f'Error: {str(e)}'
            }
    
    def _calculate_period_average(self, latitude, longitude, end_date, days, current_data):
        """Calculate average rainfall for a specific period (simplified)"""
        try:
            # Use recent historical data from current_data
            historical_values = []
            start_date = end_date - timedelta(days=days + 30)
            
            # Look at data from 30-60 days ago as baseline
            for i in range(30, 60):
                check_date = end_date - timedelta(days=i)
                if check_date in current_data:
                    val = current_data[check_date]
                    if val >= 0:
                        historical_values.append(val)
            
            if historical_values:
                return sum(historical_values) / len(historical_values)
            return 3.0  # Default for semi-arid regions
            
        except Exception as e:
            logger.error(f"Error calculating period average: {str(e)}")
            return 3.0
    
    def monitor_all_farms(self):
        """Monitor all active farms for drought conditions"""
        from core.models import Farm, DroughtEvent, Payout
        
        results = {
            'checked': 0,
            'drought_detected': 0,
            'payouts_created': 0,
            'errors': 0,
            'details': []
        }
        
        farms = Farm.objects.filter(is_active=True, is_monitored=True)
        
        for farm in farms:
            try:
                results['checked'] += 1
                
                # Check for drought
                drought_check = self.check_drought_for_farm(farm)
                
                if drought_check['is_drought']:
                    results['drought_detected'] += 1
                    
                    # Check if drought already triggered recently (last 30 days)
                    recent_drought = DroughtEvent.objects.filter(
                        farm=farm,
                        is_triggered=True,
                        triggered_at__gte=timezone.now() - timedelta(days=30)
                    ).exists()
                    
                    if not recent_drought:
                        # Create drought event
                        drought_event = DroughtEvent.objects.create(
                            farm=farm,
                            start_date=timezone.now().date() - timedelta(days=drought_check['consecutive_dry_days']),
                            consecutive_dry_days=drought_check['consecutive_dry_days'],
                            rainfall_actual_mm=drought_check['rainfall_actual'],
                            rainfall_avg_mm=drought_check['rainfall_average'],
                            is_triggered=True,
                            triggered_at=timezone.now(),
                            trigger_amount_kes=Decimal(str(farm.area_acres)) * Decimal('2500')
                        )
                        
                        # Create payout
                        payout = Payout.objects.create(
                            drought_event=drought_event,
                            farmer=farm.farmer,
                            amount_kes=drought_event.trigger_amount_kes,
                            status='pending'
                        )
                        
                        results['payouts_created'] += 1
                        results['details'].append({
                            'farm_id': farm.id,
                            'farmer': farm.farmer.name,
                            'amount': float(drought_event.trigger_amount_kes),
                            'payout_id': payout.id
                        })
                        
                        logger.info(f"Drought detected for farm {farm.id} - Payout created: {payout.id}")
                    else:
                        results['details'].append({
                            'farm_id': farm.id,
                            'status': 'Drought detected but recent payout exists (30 days)'
                        })
                        
            except Exception as e:
                results['errors'] += 1
                results['details'].append({
                    'farm_id': farm.id,
                    'error': str(e)
                })
                logger.error(f"Error monitoring farm {farm.id}: {str(e)}")
        
        return results


class RainfallDataCollector:
    """Collect and store daily rainfall data for all farms"""
    
    def __init__(self):
        self.nasa_api = NASAPowerAPI()
    
    def collect_daily_data(self, farm):
        """Collect and store today's rainfall data for a farm"""
        from core.models import RainfallRecord
        
        try:
            today = timezone.now().date()
            
            # Check if already collected today
            if RainfallRecord.objects.filter(farm=farm, date=today).exists():
                return None
            
            # Get today's rainfall
            rainfall_data = self.nasa_api.get_daily_rainfall(
                farm.latitude, 
                farm.longitude, 
                today - timedelta(days=2),
                today
            )
            
            if rainfall_data and today in rainfall_data:
                rainfall_mm = rainfall_data[today]
                
                # Get 30-year average for this date (simplified)
                avg_rainfall = self.nasa_api.get_historical_average(
                    farm.latitude, 
                    farm.longitude, 
                    today
                )
                
                # Save record
                record = RainfallRecord.objects.create(
                    farm=farm,
                    date=today,
                    rainfall_mm=rainfall_mm if rainfall_mm >= 0 else 0,
                    thirty_year_avg_mm=avg_rainfall,
                    source='NASA_POWER'
                )
                
                logger.info(f"Collected rainfall data for {farm}: {rainfall_mm}mm")
                return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error collecting rainfall for farm {farm.id}: {str(e)}")
            return None
    
    def collect_all_farms(self):
        """Collect rainfall data for all active farms"""
        from core.models import Farm
        
        results = {
            'total': 0,
            'collected': 0,
            'errors': 0
        }
        
        farms = Farm.objects.filter(is_active=True, is_monitored=True)
        results['total'] = farms.count()
        
        for farm in farms:
            try:
                record = self.collect_daily_data(farm)
                if record:
                    results['collected'] += 1
            except Exception as e:
                results['errors'] += 1
                logger.error(f"Error collecting for farm {farm.id}: {str(e)}")
        
        return results