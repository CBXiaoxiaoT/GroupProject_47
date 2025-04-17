import geocoder
from datetime import datetime, timezone, timedelta

from PyQt6.QtCore import QDate
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class LocationCache:
    _instance = None
    _last_update = None
    _current_location = ()  # 默认坐标
    _current_city = "Unknown"  # 默认城市名称

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
                # 仅在坐标变化时更新城市信息
                if (new_lat, new_lon) != self._current_location:
                    self._current_location = (new_lat, new_lon)
                    self._current_city = self._get_city_name(new_lat, new_lon)
                self._last_update = datetime.now()
        except Exception as e:
            print(f"定位服务不可用: {str(e)}")

    def _get_city_name(self, latitude, longitude):
        """通过坐标反向查询城市名称"""
        geolocator = Nominatim(user_agent="geo_locator_app")
        try:
            location = geolocator.reverse(
                (latitude, longitude),
                exactly_one=True,
                language='en'
            )

            if location:
                address = location.raw.get('address', {})
                # 按优先级搜索不同行政级别名称
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
            print(f"地理编码服务错误: {e}")
            return 'Unknown'
        except Exception as e:
            print(f"未知错误: {e}")
            return 'Unknown'

def get_location() -> tuple:
    return LocationCache().location

def get_city() -> str:
    return LocationCache().city

def get_current_time() -> tuple:
    """跨平台时间格式化"""
    now = datetime.now()
    # 手动处理日期部分（兼容所有操作系统）
    time_str = now.strftime("%H:%M")
    year = now.year
    month = now.month  # 直接获取整数，无前导零
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