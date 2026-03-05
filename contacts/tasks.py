from celery import shared_task
import requests
from .models import Contact
import logging
from celery.utils.log import get_task_logger
from django.core.cache import cache

logger = get_task_logger(__name__)

@shared_task(bind=True, ignore_result=True, max_retries=2, rate_limit = '1/s')
def get_geo_data(self, contact_id, city):
    """
    Asynchronous task to fetch and update contact coordinates via Nominatim API.
    
    Features:
        - Rate limited to 1 request per second.
        - Automatic retries with a 20-second delay upon failure.
        - Updates contact latitude and longitude based on the provided city name.
    """
    try:
        contact = Contact.objects.filter(pk=contact_id).first()
        try:
            response = requests.get(f'https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1',
                headers={"User-Agent": "ContactAppProject/1.0"},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Response status code: {response.status_code}")
            response_data = response.json()

            if response_data:
                contact.latitude = round(float(response_data[0]["lat"]), 2)
                contact.longitude = round(float(response_data[0]["lon"]), 2)
                logger.info(f"Saved coord for: {city}")
            else:
                logger.warning(f"No coords for: {city}")
        except requests.RequestException:
            contact.latitude = None
            contact.longitude = None

        contact.save()
    except Exception as e: 
        logger.error(f"Exception: {e}")
        raise self.retry(exc=e, countdown=20)
    
@shared_task(bind=True, ignore_result=True, max_retries=2, rate_limit = '1/s')
def get_weather_data(self, cache_key, lat, lon):
    """
    Asynchronous task to fetch current weather data and store it in cache.
    
    Features:
        - Rate limited to 1 request per second.
        - Automatic retries with a 20-second delay upon failure.
        - Updates weather data based on the provided latitude and longitude.
        - Formats and stores the result in Redis with a 30-minute expiration.
    """
    if lat is None or lon is None:
        logger.warning(f"Zadanie przerwane: Brak współrzędnych dla klucza {cache_key}")
        return
    
    try:
        response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,is_day,rain,cloud_cover')
        response.raise_for_status()
        logger.info(f"Response status code: {response.status_code}")
        data = response.json()
        weather = {
                'temperature': data['current']['temperature_2m'],
                'humidity': data['current']['relative_humidity_2m'],
                'windspeed': data['current']['wind_speed_10m'],
                'is_day': data['current']['is_day'],
                'rain': data['current']['rain'],
                'cloud_cover': data['current']['cloud_cover'],
            }
        cache.set(cache_key, weather, timeout=1800)

    except requests.RequestException as e:
        logger.error(f"Exception: {e}")
        raise self.retry(exc=e, countdown=20)
