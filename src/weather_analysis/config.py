"""
配置文件 - 存放API金鑰和系統設定
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


def get_env_api_key(key_name, placeholder=""):
    """
    統一取得 API Key，優先順序：
    1. 環境變數 (.env)
    2. Streamlit Cloud secrets (st.secrets)

    Args:
        key_name: 環境變數名稱
        placeholder: 預設的佔位值（用來判斷是否已設定）

    Returns:
        str: API Key 值，未設定時回傳空字串
    """
    # 1. 環境變數
    value = os.getenv(key_name, "")
    if value and value != placeholder:
        return value

    # 2. Streamlit secrets
    try:
        import streamlit as st
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass

    return ""


# OpenWeatherMap API設定
OPENWEATHER_API_KEY = get_env_api_key("OPENWEATHER_API_KEY", "your_api_key_here")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# One Call API 3.0 設定（付費，可選）
ONECALL_API_KEY = get_env_api_key("ONECALL_API_KEY", "")
ONECALL_BASE_URL = "https://api.openweathermap.org/data/3.0"

# OpenAI API設定
OPENAI_API_KEY = get_env_api_key("OPENAI_API_KEY", "your_openai_api_key_here")
OPENAI_MODEL = "gpt-4o-mini"

# 台灣主要城市列表（使用OpenWeatherMap的城市名稱）
TAIWAN_CITIES = {
    "台北": "Taipei",
    "新北": "New Taipei",
    "桃園": "Taoyuan",
    "台中": "Taichung",
    "台南": "Tainan",
    "高雄": "Kaohsiung",
    "基隆": "Keelung",
    "新竹": "Hsinchu",
    "嘉義": "Chiayi",
    "宜蘭": "Yilan",
    "花蓮": "Hualien",
    "台東": "Taitung",
}

# 雙語城市名稱對照（供 i18n 使用）
TAIWAN_CITIES_I18N = {
    "Taipei":    {"zh_tw": "台北",  "en": "Taipei"},
    "New Taipei":{"zh_tw": "新北",  "en": "New Taipei"},
    "Taoyuan":   {"zh_tw": "桃園",  "en": "Taoyuan"},
    "Taichung":  {"zh_tw": "台中",  "en": "Taichung"},
    "Tainan":    {"zh_tw": "台南",  "en": "Tainan"},
    "Kaohsiung": {"zh_tw": "高雄",  "en": "Kaohsiung"},
    "Keelung":   {"zh_tw": "基隆",  "en": "Keelung"},
    "Hsinchu":   {"zh_tw": "新竹",  "en": "Hsinchu"},
    "Chiayi":    {"zh_tw": "嘉義",  "en": "Chiayi"},
    "Yilan":     {"zh_tw": "宜蘭",  "en": "Yilan"},
    "Hualien":   {"zh_tw": "花蓮",  "en": "Hualien"},
    "Taitung":   {"zh_tw": "台東",  "en": "Taitung"},
}

# 台灣 12 城市座標（供 One Call API 使用）
TAIWAN_CITIES_COORDS = {
    "Taipei":     {"lat": 25.0330, "lon": 121.5654},
    "New Taipei": {"lat": 25.0120, "lon": 121.4650},
    "Taoyuan":    {"lat": 24.9936, "lon": 121.3010},
    "Taichung":   {"lat": 24.1477, "lon": 120.6736},
    "Tainan":     {"lat": 22.9999, "lon": 120.2269},
    "Kaohsiung":  {"lat": 22.6273, "lon": 120.3014},
    "Keelung":    {"lat": 25.1276, "lon": 121.7392},
    "Hsinchu":    {"lat": 24.8138, "lon": 120.9675},
    "Chiayi":     {"lat": 23.4800, "lon": 120.4491},
    "Yilan":      {"lat": 24.7570, "lon": 121.7533},
    "Hualien":    {"lat": 23.9910, "lon": 121.6113},
    "Taitung":    {"lat": 22.7583, "lon": 121.1444},
}

# 系統設定
CACHE_EXPIRE_MINUTES = 15  # 快取過期時間
DEFAULT_CITY = "台北"
FORECAST_DAYS = 5

# 單位設定
UNITS = "metric"  # metric = 攝氏度, imperial = 華氏度
LANG = "zh_tw"    # 語言設定（OWM API 預設值，實際會依 i18n 動態切換）

# AI分析設定
AI_MAX_TOKENS = 1000  # AI回應的最大token數
