"""
空氣品質 AQI 模組 - 整合環境部開放資料 API
"""
import requests
import streamlit as st

AQI_API_URL = "https://data.moenv.gov.tw/api/v2/aqx_p_432"

# 英文城市名 → 環境部 County 欄位值
CITY_COUNTY_MAP = {
    "Taipei": "臺北市",
    "New Taipei": "新北市",
    "Taoyuan": "桃園市",
    "Taichung": "臺中市",
    "Tainan": "臺南市",
    "Kaohsiung": "高雄市",
    "Keelung": "基隆市",
    "Hsinchu": "新竹市",
    "Chiayi": "嘉義市",
    "Yilan": "宜蘭縣",
    "Hualien": "花蓮縣",
    "Taitung": "臺東縣",
}


@st.cache_data(ttl=30 * 60, show_spinner=False)
def fetch_aqi_data(api_key: str) -> list[dict] | None:
    """
    取得全台 AQI 資料（快取 30 分鐘）。

    Returns:
        list[dict] | None: 測站資料列表，失敗時回傳 None
    """
    try:
        params = {
            "api_key": api_key,
            "limit": 1000,
            "sort": "ImportDate desc",
            "format": "JSON",
        }
        resp = requests.get(AQI_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # API 可能回傳 list 或 {"records": list}
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get("records", [])
        else:
            return None
        if not records:
            return None
        return records
    except Exception:
        return None


def get_city_aqi(all_data: list[dict], city_en: str) -> dict | None:
    """
    從全台資料中取得指定城市的代表測站 AQI。
    同縣市多站取 AQI 最高的那站（保守原則）。

    Returns:
        dict | None: {"station", "aqi", "pm25", "pm10", "o3", "county", "pollutant", "status"}
    """
    county = CITY_COUNTY_MAP.get(city_en)
    if not county or not all_data:
        return None

    city_stations = [r for r in all_data if r.get("county") == county]
    if not city_stations:
        return None

    # 取 AQI 最高的測站
    def _parse_aqi(record):
        try:
            return int(record.get("aqi", 0))
        except (ValueError, TypeError):
            return 0

    best = max(city_stations, key=_parse_aqi)
    aqi_val = _parse_aqi(best)

    def _safe_float(val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    return {
        "station": best.get("sitename", ""),
        "aqi": aqi_val,
        "pm25": _safe_float(best.get("pm2.5", best.get("pm25"))),
        "pm10": _safe_float(best.get("pm10")),
        "o3": _safe_float(best.get("o3")),
        "county": county,
        "pollutant": best.get("pollutant", ""),
        "status": best.get("status", ""),
    }


def get_aqi_level(aqi: int) -> tuple[str, str]:
    """
    回傳 (等級 i18n key, 顏色 hex)。

    AQI 分級：
    0-50: 良好 (green)
    51-100: 普通 (yellow)
    101-150: 對敏感族群不健康 (orange)
    151-200: 不健康 (red)
    201-300: 非常不健康 (purple)
    301+: 危害 (maroon)
    """
    if aqi <= 50:
        return "aqi.level_good", "#00e400"
    elif aqi <= 100:
        return "aqi.level_moderate", "#ffff00"
    elif aqi <= 150:
        return "aqi.level_sensitive", "#ff7e00"
    elif aqi <= 200:
        return "aqi.level_unhealthy", "#ff0000"
    elif aqi <= 300:
        return "aqi.level_very_unhealthy", "#8f3f97"
    else:
        return "aqi.level_hazardous", "#7e0023"


def get_all_cities_aqi(all_data: list[dict]) -> list[dict]:
    """
    取得所有 12 城市的 AQI 資料，回傳列表（按 AQI 降序）。
    """
    results = []
    for city_en, county in CITY_COUNTY_MAP.items():
        info = get_city_aqi(all_data, city_en)
        if info:
            info["city_en"] = city_en
            results.append(info)
    results.sort(key=lambda x: x["aqi"], reverse=True)
    return results
