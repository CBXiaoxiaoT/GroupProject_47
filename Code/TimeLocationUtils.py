import geocoder
from datetime import datetime, timezone, timedelta

from PyQt6.QtCore import QDate
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class LocationCache:
    _instance = None
    _last_update = None
    _current_location = ()  # default coordinate
    _current_city = "Unknown"  # default city name

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def location(self):
        now = datetime.now()
        if not self._last_update or (now - self._last_update) > timedelta(hours=1):
            self._refresh_location()
        return self._current_location

    @property
    def city(self):
        now = datetime.now()
        if not self._last_update or (now - self._last_update) > timedelta(hours=1):
            self._refresh_location()
        return self._current_city

    def _refresh_location(self):
        try:
            if g := geocoder.ip('me'):
                new_lat, new_lon = g.latlng
                # only update city infor when coordinate changes
                if (new_lat, new_lon) != self._current_location:
                    self._current_location = (new_lat, new_lon)
                    self._current_city = self._get_city_name(new_lat, new_lon)
                self._last_update = datetime.now()
        except Exception as e:
            print(f"Location service unavailable: {str(e)}")

    def _get_city_name(self, latitude, longitude):
        """Reverse geocode coordinates to retrieve city name"""
        geolocator = Nominatim(user_agent="geo_locator_app")
        try:
            location = geolocator.reverse(
                (latitude, longitude),
                exactly_one=True,
                language='en'
            )

            if location:
                address = location.raw.get('address', {})
                # Search through administrative levels in order of priority
                city_keys = [
                    'city', 'town', 'village',
                    'municipality', 'county',
                    'state', 'region'
                ]
                for key in city_keys:
                    if key in address:
                        return address[key]
                return address.get('state', 'Unknown')
            return 'Unknown'
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding service error: {e}")
            return 'Unknown'
        except Exception as e:
            print(f"Unknown error: {e}")
            return 'Unknown'

def get_location() -> tuple:
    return LocationCache().location

def get_city() -> str:
    return LocationCache().city

def get_current_time() -> tuple:
    """Cross-platform time formatting"""
    now = datetime.now()
    # Manually handle date part for cross-platform compatibility
    time_str = now.strftime("%H:%M")
    year = now.year
    month = now.month  # Retrieve integer values without leading zeros
    day = now.day
    date_str = f"{year}/{month}/{day}"
    return time_str, date_str

def get_utc_time() -> dict:
    utc_now = datetime.now(timezone.utc)
    return {
        "utc_time": utc_now,
        "decimal_utc": utc_now.hour + utc_now.minute/60,
        "year_day": utc_now.timetuple().tm_yday
    }
def get_today_date() -> QDate:
    now = datetime.now()
    return QDate(now.year, now.month, now.day)