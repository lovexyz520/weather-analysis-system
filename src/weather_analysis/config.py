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

# 系統設定
CACHE_EXPIRE_MINUTES = 15  # 快取過期時間
DEFAULT_CITY = "台北"
FORECAST_DAYS = 5

# 單位設定
UNITS = "metric"  # metric = 攝氏度, imperial = 華氏度
LANG = "zh_tw"    # 語言設定

# AI分析設定
AI_MAX_TOKENS = 1000  # AI回應的最大token數
