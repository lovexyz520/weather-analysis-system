"""
天氣API整合模組 - 與OpenWeatherMap API互動
"""
import requests
import streamlit as st
from datetime import datetime, timedelta
from weather_analysis import config


class WeatherAPI:
    """天氣API整合類別"""

    def __init__(self, api_key=None):
        self.api_key = api_key or config.OPENWEATHER_API_KEY
        self.base_url = config.OPENWEATHER_BASE_URL
        self.units = config.UNITS
        self.lang = config.LANG

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
                return True, "API Key 有效"
            if resp.status_code == 401:
                return False, "API Key 無效或尚未啟用"
            return False, f"驗證失敗 (HTTP {resp.status_code})"
        except requests.exceptions.Timeout:
            return False, "連線逾時，請稍後再試"
        except requests.exceptions.RequestException as e:
            return False, f"網路錯誤: {e}"

    # ── 資料查詢（帶快取） ──

    def get_current_weather(self, city):
        """取得即時天氣資料（透過快取層）"""
        return _cached_current_weather(self.api_key, city)

    def get_forecast(self, city, days=5):
        """取得天氣預報資料（透過快取層）"""
        return _cached_forecast(self.api_key, city)

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

    def _get_tw_city_name(self, city_en):
        """取得中文城市名稱"""
        for tw, en in config.TAIWAN_CITIES.items():
            if en == city_en:
                return tw
        return city_en

    @staticmethod
    def get_weather_icon_url(icon_code):
        """取得天氣圖示URL"""
        return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"


# ── 快取函式（模組層級，供 @st.cache_data 使用） ──

@st.cache_data(ttl=config.CACHE_EXPIRE_MINUTES * 60, show_spinner=False)
def _cached_current_weather(api_key, city):
    """快取即時天氣（TTL 15 分鐘）"""
    try:
        url = f"{config.OPENWEATHER_BASE_URL}/weather"
        params = {
            'q': f"{city},TW",
            'appid': api_key,
            'units': config.UNITS,
            'lang': config.LANG,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 取得中文城市名
        city_tw = city
        for tw, en in config.TAIWAN_CITIES.items():
            if en == city:
                city_tw = tw
                break

        return {
            'city': city,
            'city_tw': city_tw,
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
        st.error(f"API 請求錯誤: {e}")
        return None
    except KeyError as e:
        st.error(f"資料解析錯誤: {e}")
        return None


@st.cache_data(ttl=config.CACHE_EXPIRE_MINUTES * 60, show_spinner=False)
def _cached_forecast(api_key, city):
    """快取預報資料（TTL 15 分鐘）"""
    try:
        url = f"{config.OPENWEATHER_BASE_URL}/forecast"
        params = {
            'q': f"{city},TW",
            'appid': api_key,
            'units': config.UNITS,
            'lang': config.LANG,
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
        st.error(f"API 請求錯誤: {e}")
        return None
    except KeyError as e:
        st.error(f"資料解析錯誤: {e}")
        return None
