"""
警報模組測試 - evaluate_alerts
"""
import pytest
from weather_analysis.alerts import evaluate_alerts, AlertSeverity, WeatherAlert


def _make_weather(temp=25, humidity=60, wind=3):
    """建立模擬即時天氣 dict"""
    return {"temperature": temp, "humidity": humidity, "wind_speed": wind}


def _make_daily(pop_max=10, temp_max=28, temp_min=22):
    """建立模擬每日摘要 list"""
    return [{"pop_max": pop_max, "temp_max": temp_max, "temp_min": temp_min}]


class TestEvaluateAlerts:
    """evaluate_alerts 警報觸發測試"""

    def test_normal_weather_no_alerts(self):
        """正常天氣 → 0 個警報"""
        alerts = evaluate_alerts(_make_weather(), _make_daily())
        assert len(alerts) == 0

    def test_none_weather(self):
        """current_weather 為 None → 空列表"""
        assert evaluate_alerts(None, _make_daily()) == []

    # ── 溫度警報 ──

    def test_extreme_heat(self):
        """溫度 > 36°C → DANGER 極端高溫"""
        alerts = evaluate_alerts(_make_weather(temp=38), _make_daily())
        heat_alerts = [a for a in alerts if a.title_key == "alert.extreme_heat_title"]
        assert len(heat_alerts) == 1
        assert heat_alerts[0].severity == AlertSeverity.DANGER
        assert heat_alerts[0].value == 38
        assert heat_alerts[0].threshold == 36

    def test_high_temp(self):
        """溫度 > 33°C (<=36) → CAUTION 高溫"""
        alerts = evaluate_alerts(_make_weather(temp=35), _make_daily())
        high_temp = [a for a in alerts if a.title_key == "alert.high_temp_title"]
        assert len(high_temp) == 1
        assert high_temp[0].severity == AlertSeverity.CAUTION

    def test_extreme_heat_overrides_high_temp(self):
        """極端高溫 → 不重複觸發一般高溫"""
        alerts = evaluate_alerts(_make_weather(temp=38), _make_daily())
        high_temp = [a for a in alerts if a.title_key == "alert.high_temp_title"]
        assert len(high_temp) == 0

    def test_extreme_cold(self):
        """溫度 < 5°C → DANGER 極端低溫"""
        alerts = evaluate_alerts(_make_weather(temp=3), _make_daily())
        cold_alerts = [a for a in alerts if a.title_key == "alert.extreme_cold_title"]
        assert len(cold_alerts) == 1
        assert cold_alerts[0].severity == AlertSeverity.DANGER

    def test_low_temp(self):
        """溫度 < 10°C (>=5) → CAUTION 低溫"""
        alerts = evaluate_alerts(_make_weather(temp=8), _make_daily())
        low_temp = [a for a in alerts if a.title_key == "alert.low_temp_title"]
        assert len(low_temp) == 1
        assert low_temp[0].severity == AlertSeverity.CAUTION

    def test_extreme_cold_overrides_low_temp(self):
        """極端低溫 → 不重複觸發一般低溫"""
        alerts = evaluate_alerts(_make_weather(temp=3), _make_daily())
        low_temp = [a for a in alerts if a.title_key == "alert.low_temp_title"]
        assert len(low_temp) == 0

    # ── 風速警報 ──

    def test_strong_wind(self):
        """風速 > 15 m/s → DANGER"""
        alerts = evaluate_alerts(_make_weather(wind=18), _make_daily())
        wind_alerts = [a for a in alerts if a.title_key == "alert.strong_wind_title"]
        assert len(wind_alerts) == 1
        assert wind_alerts[0].severity == AlertSeverity.DANGER

    def test_high_wind(self):
        """風速 > 10 m/s (<=15) → CAUTION"""
        alerts = evaluate_alerts(_make_weather(wind=12), _make_daily())
        wind_alerts = [a for a in alerts if a.title_key == "alert.high_wind_title"]
        assert len(wind_alerts) == 1
        assert wind_alerts[0].severity == AlertSeverity.CAUTION

    # ── 濕度警報 ──

    def test_high_humidity(self):
        """濕度 > 90% → CAUTION"""
        alerts = evaluate_alerts(_make_weather(humidity=95), _make_daily())
        hum_alerts = [a for a in alerts if a.title_key == "alert.high_humidity_title"]
        assert len(hum_alerts) == 1
        assert hum_alerts[0].severity == AlertSeverity.CAUTION

    def test_normal_humidity_no_alert(self):
        """濕度 90% → 不觸發"""
        alerts = evaluate_alerts(_make_weather(humidity=90), _make_daily())
        hum_alerts = [a for a in alerts if a.title_key == "alert.high_humidity_title"]
        assert len(hum_alerts) == 0

    # ── 降雨警報 ──

    def test_heavy_rain(self):
        """降雨 > 80% → DANGER"""
        alerts = evaluate_alerts(_make_weather(), _make_daily(pop_max=90))
        rain_alerts = [a for a in alerts if a.title_key == "alert.heavy_rain_title"]
        assert len(rain_alerts) == 1
        assert rain_alerts[0].severity == AlertSeverity.DANGER

    def test_moderate_rain(self):
        """降雨 > 60% (<=80) → CAUTION"""
        alerts = evaluate_alerts(_make_weather(), _make_daily(pop_max=70))
        rain_alerts = [a for a in alerts if a.title_key == "alert.rain_title"]
        assert len(rain_alerts) == 1
        assert rain_alerts[0].severity == AlertSeverity.CAUTION

    def test_heavy_rain_overrides_moderate(self):
        """暴雨 → 不重複觸發一般降雨"""
        alerts = evaluate_alerts(_make_weather(), _make_daily(pop_max=90))
        mod_rain = [a for a in alerts if a.title_key == "alert.rain_title"]
        assert len(mod_rain) == 0

    # ── 日溫差警報 ──

    def test_temp_swing(self):
        """日溫差 > 10°C → CAUTION"""
        alerts = evaluate_alerts(_make_weather(), _make_daily(temp_max=32, temp_min=18))
        swing = [a for a in alerts if a.title_key == "alert.temp_swing_title"]
        assert len(swing) == 1
        assert swing[0].value == 14

    def test_normal_temp_swing(self):
        """日溫差 <= 10°C → 不觸發"""
        alerts = evaluate_alerts(_make_weather(), _make_daily(temp_max=28, temp_min=22))
        swing = [a for a in alerts if a.title_key == "alert.temp_swing_title"]
        assert len(swing) == 0

    # ── 多重警報 ──

    def test_multiple_alerts(self):
        """極端天氣 → 多個警報同時觸發"""
        weather = _make_weather(temp=38, humidity=95, wind=18)
        daily = _make_daily(pop_max=90, temp_max=40, temp_min=25)
        alerts = evaluate_alerts(weather, daily)
        # 極端高溫 + 強風 + 高濕 + 暴雨 + 溫差 = 5
        assert len(alerts) == 5

    def test_no_daily_summary(self):
        """daily_summary 為 None → 不觸發降雨/溫差警報"""
        alerts = evaluate_alerts(_make_weather(temp=38), None)
        # 只有極端高溫
        assert len(alerts) == 1
        assert alerts[0].title_key == "alert.extreme_heat_title"

    # ── 邊界值 ──

    def test_boundary_temp_36(self):
        """溫度 = 36°C → 不觸發極端高溫（需 > 36）"""
        alerts = evaluate_alerts(_make_weather(temp=36), _make_daily())
        heat = [a for a in alerts if a.title_key == "alert.extreme_heat_title"]
        assert len(heat) == 0

    def test_boundary_temp_33(self):
        """溫度 = 33°C → 不觸發高溫（需 > 33）"""
        alerts = evaluate_alerts(_make_weather(temp=33), _make_daily())
        high = [a for a in alerts if a.title_key == "alert.high_temp_title"]
        assert len(high) == 0

    def test_boundary_wind_15(self):
        """風速 = 15 m/s → 不觸發強風（需 > 15）"""
        alerts = evaluate_alerts(_make_weather(wind=15), _make_daily())
        strong = [a for a in alerts if a.title_key == "alert.strong_wind_title"]
        assert len(strong) == 0


class TestWeatherAlertDataclass:
    """WeatherAlert dataclass 基本測試"""

    def test_create_alert(self):
        alert = WeatherAlert(
            severity=AlertSeverity.DANGER,
            title_key="alert.test",
            message_key="alert.test_msg",
            icon="⚠️",
            value=38.5,
            threshold=36,
        )
        assert alert.severity == AlertSeverity.DANGER
        assert alert.value == 38.5

    def test_alert_severity_values(self):
        assert AlertSeverity.CAUTION.value == "caution"
        assert AlertSeverity.DANGER.value == "danger"
