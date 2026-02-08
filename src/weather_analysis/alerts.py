"""
天氣警報模組 - 規則引擎警報 + One Call API 3.0 官方警報
"""
from dataclasses import dataclass
from enum import Enum

import requests
from weather_analysis import config
from weather_analysis.i18n import t


class AlertSeverity(Enum):
    CAUTION = "caution"  # 黃色 st.warning
    DANGER = "danger"    # 紅色 st.error


@dataclass
class WeatherAlert:
    severity: AlertSeverity
    title_key: str      # i18n key
    message_key: str    # i18n key
    icon: str
    value: float
    threshold: float


def evaluate_alerts(current_weather, daily_summary) -> list[WeatherAlert]:
    """
    規則引擎警報（免費 API 資料）

    根據即時天氣與每日摘要資料，判斷是否需要發出警報。
    """
    alerts = []
    if not current_weather:
        return alerts

    temp = current_weather["temperature"]
    humidity = current_weather["humidity"]
    wind = current_weather["wind_speed"]

    # 取得今日降雨機率（從 daily_summary）
    today_pop = 0
    if daily_summary:
        today_pop = daily_summary[0].get("pop_max", 0)

    # ── 極端高溫 >36°C (DANGER) ──
    if temp > 36:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.DANGER,
            title_key="alert.extreme_heat_title",
            message_key="alert.extreme_heat_msg",
            icon="🔥",
            value=temp,
            threshold=36,
        ))
    # ── 高溫 >33°C (CAUTION) ──
    elif temp > 33:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.CAUTION,
            title_key="alert.high_temp_title",
            message_key="alert.high_temp_msg",
            icon="🌡️",
            value=temp,
            threshold=33,
        ))

    # ── 極端低溫 <5°C (DANGER) ──
    if temp < 5:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.DANGER,
            title_key="alert.extreme_cold_title",
            message_key="alert.extreme_cold_msg",
            icon="🥶",
            value=temp,
            threshold=5,
        ))
    # ── 低溫 <10°C (CAUTION) ──
    elif temp < 10:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.CAUTION,
            title_key="alert.low_temp_title",
            message_key="alert.low_temp_msg",
            icon="❄️",
            value=temp,
            threshold=10,
        ))

    # ── 強風 >15 m/s (DANGER) ──
    if wind > 15:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.DANGER,
            title_key="alert.strong_wind_title",
            message_key="alert.strong_wind_msg",
            icon="🌪️",
            value=wind,
            threshold=15,
        ))
    # ── 大風 >10 m/s (CAUTION) ──
    elif wind > 10:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.CAUTION,
            title_key="alert.high_wind_title",
            message_key="alert.high_wind_msg",
            icon="💨",
            value=wind,
            threshold=10,
        ))

    # ── 高濕 >90% (CAUTION) ──
    if humidity > 90:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.CAUTION,
            title_key="alert.high_humidity_title",
            message_key="alert.high_humidity_msg",
            icon="💧",
            value=humidity,
            threshold=90,
        ))

    # ── 暴雨 pop>80% (DANGER) ──
    if today_pop > 80:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.DANGER,
            title_key="alert.heavy_rain_title",
            message_key="alert.heavy_rain_msg",
            icon="⛈️",
            value=today_pop,
            threshold=80,
        ))
    # ── 降雨 pop>60% (CAUTION) ──
    elif today_pop > 60:
        alerts.append(WeatherAlert(
            severity=AlertSeverity.CAUTION,
            title_key="alert.rain_title",
            message_key="alert.rain_msg",
            icon="🌧️",
            value=today_pop,
            threshold=60,
        ))

    # ── 日溫差 >10°C (CAUTION) ──
    if daily_summary:
        day = daily_summary[0]
        temp_swing = day["temp_max"] - day["temp_min"]
        if temp_swing > 10:
            alerts.append(WeatherAlert(
                severity=AlertSeverity.CAUTION,
                title_key="alert.temp_swing_title",
                message_key="alert.temp_swing_msg",
                icon="🌡️",
                value=round(temp_swing, 1),
                threshold=10,
            ))

    return alerts


def evaluate_onecall_alerts(api_key, lat, lon) -> list[WeatherAlert]:
    """
    One Call API 3.0 官方警報（付費 API）

    呼叫 /data/3.0/onecall 取得 alerts 欄位。
    """
    if not api_key:
        return []

    try:
        url = f"{config.ONECALL_BASE_URL}/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "exclude": "minutely,hourly,daily",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        alerts = []
        for item in data.get("alerts", []):
            alerts.append(WeatherAlert(
                severity=AlertSeverity.DANGER,
                title_key="alert.official_title",
                message_key="",  # 使用 raw message
                icon="⚠️",
                value=0,
                threshold=0,
            ))
            # 覆寫 message_key 為實際文字（官方警報不走 i18n）
            alerts[-1]._raw_event = item.get("event", "")
            alerts[-1]._raw_description = item.get("description", "")

        return alerts
    except Exception:
        return []
