"""
天氣API整合模組 - 與OpenWeatherMap API互動
"""
import requests
import streamlit as st
from datetime import datetime, timedelta
from weather_analysis import config
from weather_analysis.i18n import t, get_lang


class WeatherAPI:
    """天氣API整合類別"""

    def __init__(self, api_key=None):
        self.api_key = api_key or config.OPENWEATHER_API_KEY
        self.base_url = config.OPENWEATHER_BASE_URL
        self.units = config.UNITS

    # ── 驗證 ──

    @staticmethod
    def validate_key(api_key):
        """
        輕量驗證 OpenWeatherMap API Key（呼叫一次即時天氣）

        Returns:
            (bool, str): (是否有效, 訊息)
        """
        try:
            url = f"{config.OPENWEATHER_BASE_URL}/weather"
            params = {
                "q": "Taipei,TW",
                "appid": api_key,
                "units": config.UNITS,
            }
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                return True, t("api.key_valid")
            if resp.status_code == 401:
                return False, t("api.key_invalid")
            return False, t("api.key_fail", code=resp.status_code)
        except requests.exceptions.Timeout:
            return False, t("api.timeout")
        except requests.exceptions.RequestException as e:
            return False, t("api.network_error", e=e)

    # ── 資料查詢（帶快取） ──

    def get_current_weather(self, city):
        """取得即時天氣資料（透過快取層）"""
        lang = get_lang()
        owm_lang = "zh_tw" if lang == "zh_tw" else "en"
        return _cached_current_weather(self.api_key, city, owm_lang)

    def get_forecast(self, city, days=5):
        """取得天氣預報資料（透過快取層）"""
        lang = get_lang()
        owm_lang = "zh_tw" if lang == "zh_tw" else "en"
        return _cached_forecast(self.api_key, city, owm_lang)

    def get_daily_forecast_summary(self, city, days=5):
        """取得每日天氣預報摘要"""
        forecast_list = self.get_forecast(city, days)
        if not forecast_list:
            return None

        # 按日期分組
        daily_data = {}
        for item in forecast_list:
            date = item['datetime'].date()
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(item)

        # 計算每日摘要
        daily_summary = []
        for date, items in sorted(daily_data.items())[:days]:
            temps = [item['temperature'] for item in items]
            summary = {
                'date': date,
                'temp_avg': round(sum(temps) / len(temps), 1),
                'temp_min': min([item['temp_min'] for item in items]),
                'temp_max': max([item['temp_max'] for item in items]),
                'humidity_avg': round(sum([item['humidity'] for item in items]) / len(items), 0),
                'pop_max': max([item['pop'] for item in items]),
                'weather': items[len(items)//2]['weather'],
                'icon': items[len(items)//2]['icon'],
                'wind_speed_avg': round(sum([item['wind_speed'] for item in items]) / len(items), 1)
            }
            daily_summary.append(summary)

        return daily_summary

    @staticmethod
    def get_city_display_name(city_en):
        """取得城市顯示名稱（依當前語言）"""
        lang = get_lang()
        entry = config.TAIWAN_CITIES_I18N.get(city_en)
        if entry:
            return entry.get(lang, city_en)
        return city_en

    @staticmethod
    def get_weather_icon_url(icon_code):
        """取得天氣圖示URL"""
        return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"


# ── 快取函式（模組層級，供 @st.cache_data 使用） ──

@st.cache_data(ttl=config.CACHE_EXPIRE_MINUTES * 60, show_spinner=False)
def _cached_current_weather(api_key, city, lang):
    """快取即時天氣（TTL 15 分鐘）"""
    try:
        url = f"{config.OPENWEATHER_BASE_URL}/weather"
        params = {
            'q': f"{city},TW",
            'appid': api_key,
            'units': config.UNITS,
            'lang': lang,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 取得顯示用城市名稱
        city_display = WeatherAPI.get_city_display_name(city)

        return {
            'city': city,
            'city_tw': city_display,
            'temperature': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'temp_min': round(data['main']['temp_min'], 1),
            'temp_max': round(data['main']['temp_max'], 1),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'weather': data['weather'][0]['description'],
            'weather_main': data['weather'][0]['main'],
            'icon': data['weather'][0]['icon'],
            'wind_speed': round(data['wind']['speed'], 1),
            'clouds': data['clouds']['all'],
            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(data['sys']['sunset']),
            'timestamp': datetime.fromtimestamp(data['dt']),
        }
    except requests.exceptions.RequestException as e:
        st.error(t("api.error_request", e=e))
        return None
    except KeyError as e:
        st.error(t("api.error_parse", e=e))
        return None


@st.cache_data(ttl=config.CACHE_EXPIRE_MINUTES * 60, show_spinner=False)
def _cached_forecast(api_key, city, lang):
    """快取預報資料（TTL 15 分鐘）"""
    try:
        url = f"{config.OPENWEATHER_BASE_URL}/forecast"
        params = {
            'q': f"{city},TW",
            'appid': api_key,
            'units': config.UNITS,
            'lang': lang,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        forecast_list = []
        for item in data['list']:
            forecast_list.append({
                'datetime': datetime.fromtimestamp(item['dt']),
                'temperature': round(item['main']['temp'], 1),
                'feels_like': round(item['main']['feels_like'], 1),
                'temp_min': round(item['main']['temp_min'], 1),
                'temp_max': round(item['main']['temp_max'], 1),
                'humidity': item['main']['humidity'],
                'weather': item['weather'][0]['description'],
                'weather_main': item['weather'][0]['main'],
                'icon': item['weather'][0]['icon'],
                'wind_speed': round(item['wind']['speed'], 1),
                'clouds': item['clouds']['all'],
                'pop': round(item.get('pop', 0) * 100, 0),
            })
        return forecast_list
    except requests.exceptions.RequestException as e:
        st.error(t("api.error_request", e=e))
        return None
    except KeyError as e:
        st.error(t("api.error_parse", e=e))
        return None


@st.cache_data(ttl=config.CACHE_EXPIRE_MINUTES * 60, show_spinner=False)
def _cached_onecall_uvi(api_key, lat, lon):
    """快取 One Call API UVI 資料（TTL 15 分鐘）"""
    try:
        url = f"{config.ONECALL_BASE_URL}/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": config.UNITS,
            "exclude": "minutely,alerts",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        return {
            "uvi": current.get("uvi", 0),
            "dt": datetime.fromtimestamp(current.get("dt", 0)),
        }
    except Exception:
        return None


def get_uv_level(uvi: float) -> tuple[str, str]:
    """
    UV 指數分級。

    Returns:
        (i18n key, 顏色 hex)
    """
    if uvi <= 2:
        return "uv.level_low", "#00e400"
    elif uvi <= 5:
        return "uv.level_moderate", "#ffff00"
    elif uvi <= 7:
        return "uv.level_high", "#ff7e00"
    elif uvi <= 10:
        return "uv.level_very_high", "#ff0000"
    else:
        return "uv.level_extreme", "#8f3f97"
