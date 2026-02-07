"""
天氣API整合模組 - 與OpenWeatherMap API互動
"""
import requests
from datetime import datetime, timedelta
from weather_analysis import config

class WeatherAPI:
    """天氣API整合類別"""
    
    def __init__(self, api_key=None):
        """
        初始化WeatherAPI
        
        Args:
            api_key: OpenWeatherMap API金鑰
        """
        self.api_key = api_key or config.OPENWEATHER_API_KEY
        self.base_url = config.OPENWEATHER_BASE_URL
        self.units = config.UNITS
        self.lang = config.LANG
        
    def get_current_weather(self, city):
        """
        取得即時天氣資料
        
        Args:
            city: 城市名稱（英文）
            
        Returns:
            dict: 天氣資料字典
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{city},TW",
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 格式化資料
            weather_data = {
                'city': city,
                'city_tw': self._get_tw_city_name(city),
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
                'timestamp': datetime.fromtimestamp(data['dt'])
            }
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"API請求錯誤: {e}")
            return None
        except KeyError as e:
            print(f"資料解析錯誤: {e}")
            return None
    
    def get_forecast(self, city, days=5):
        """
        取得天氣預報資料
        
        Args:
            city: 城市名稱（英文）
            days: 預報天數（預設5天）
            
        Returns:
            list: 預報資料列表
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': f"{city},TW",
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 處理預報資料（每3小時一筆）
            forecast_list = []
            for item in data['list']:
                forecast_data = {
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
                    'pop': round(item.get('pop', 0) * 100, 0)  # 降雨機率(%)
                }
                forecast_list.append(forecast_data)
            
            return forecast_list
            
        except requests.exceptions.RequestException as e:
            print(f"API請求錯誤: {e}")
            return None
        except KeyError as e:
            print(f"資料解析錯誤: {e}")
            return None
    
    def get_daily_forecast_summary(self, city, days=5):
        """
        取得每日天氣預報摘要（整理3小時資料為每日資料）
        
        Args:
            city: 城市名稱（英文）
            days: 預報天數
            
        Returns:
            list: 每日預報摘要
        """
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
                'pop_max': max([item['pop'] for item in items]),  # 最高降雨機率
                'weather': items[len(items)//2]['weather'],  # 取中間時段的天氣
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
        """
        取得天氣圖示URL
        
        Args:
            icon_code: 天氣圖示代碼
            
        Returns:
            str: 圖示URL
        """
        return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
