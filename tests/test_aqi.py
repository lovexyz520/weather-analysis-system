"""
AQI 模組測試 - get_aqi_level, get_city_aqi, get_all_cities_aqi
"""
import pytest
from weather_analysis.aqi_api import get_aqi_level, get_city_aqi, get_all_cities_aqi


# ── get_aqi_level ──


class TestGetAqiLevel:
    """AQI 分級測試（6 級）"""

    @pytest.mark.parametrize("aqi,expected_key,expected_color", [
        (0, "aqi.level_good", "#00e400"),
        (25, "aqi.level_good", "#00e400"),
        (50, "aqi.level_good", "#00e400"),
        (51, "aqi.level_moderate", "#ffff00"),
        (100, "aqi.level_moderate", "#ffff00"),
        (101, "aqi.level_sensitive", "#ff7e00"),
        (150, "aqi.level_sensitive", "#ff7e00"),
        (151, "aqi.level_unhealthy", "#ff0000"),
        (200, "aqi.level_unhealthy", "#ff0000"),
        (201, "aqi.level_very_unhealthy", "#8f3f97"),
        (300, "aqi.level_very_unhealthy", "#8f3f97"),
        (301, "aqi.level_hazardous", "#7e0023"),
        (500, "aqi.level_hazardous", "#7e0023"),
    ])
    def test_aqi_levels(self, aqi, expected_key, expected_color):
        key, color = get_aqi_level(aqi)
        assert key == expected_key
        assert color == expected_color

    def test_boundary_50_51(self):
        """50/51 邊界"""
        assert get_aqi_level(50)[0] == "aqi.level_good"
        assert get_aqi_level(51)[0] == "aqi.level_moderate"

    def test_boundary_300_301(self):
        """300/301 邊界"""
        assert get_aqi_level(300)[0] == "aqi.level_very_unhealthy"
        assert get_aqi_level(301)[0] == "aqi.level_hazardous"


# ── get_city_aqi ──


class TestGetCityAqi:
    """城市 AQI 查詢測試"""

    SAMPLE_DATA = [
        {"county": "臺北市", "sitename": "中山", "aqi": "45", "pm2.5": "12.3", "pm10": "25", "o3": "30", "pollutant": "PM2.5", "status": "良好"},
        {"county": "臺北市", "sitename": "萬華", "aqi": "60", "pm2.5": "18.5", "pm10": "35", "o3": "40", "pollutant": "PM2.5", "status": "普通"},
        {"county": "高雄市", "sitename": "前鎮", "aqi": "120", "pm2.5": "55.2", "pm10": "80", "o3": "65", "pollutant": "PM2.5", "status": "不健康"},
    ]

    def test_taipei_highest_station(self):
        """臺北市有 2 站 → 取 AQI 較高的萬華站"""
        result = get_city_aqi(self.SAMPLE_DATA, "Taipei")
        assert result is not None
        assert result["station"] == "萬華"
        assert result["aqi"] == 60

    def test_kaohsiung(self):
        """高雄市 → 前鎮站"""
        result = get_city_aqi(self.SAMPLE_DATA, "Kaohsiung")
        assert result is not None
        assert result["aqi"] == 120

    def test_unknown_city(self):
        """未知城市 → None"""
        assert get_city_aqi(self.SAMPLE_DATA, "Tokyo") is None

    def test_no_data_for_city(self):
        """資料中無該城市 → None"""
        assert get_city_aqi(self.SAMPLE_DATA, "Taichung") is None

    def test_empty_data(self):
        """空資料 → None"""
        assert get_city_aqi([], "Taipei") is None

    def test_none_data(self):
        """None 資料 → None"""
        assert get_city_aqi(None, "Taipei") is None

    def test_pm25_field_name(self):
        """pm2.5 欄位正確解析"""
        result = get_city_aqi(self.SAMPLE_DATA, "Taipei")
        assert result["pm25"] == 18.5

    def test_pm10_and_o3(self):
        """pm10 和 o3 正確解析"""
        result = get_city_aqi(self.SAMPLE_DATA, "Kaohsiung")
        assert result["pm10"] == 80.0
        assert result["o3"] == 65.0

    def test_invalid_aqi_value(self):
        """AQI 為非數字 → 預設 0"""
        data = [{"county": "臺北市", "sitename": "X", "aqi": "N/A"}]
        result = get_city_aqi(data, "Taipei")
        assert result["aqi"] == 0


# ── get_all_cities_aqi ──


class TestGetAllCitiesAqi:
    """全城市 AQI 排行測試"""

    def test_sorted_descending(self):
        """結果按 AQI 降序"""
        data = [
            {"county": "臺北市", "sitename": "A", "aqi": "45", "pollutant": "", "status": ""},
            {"county": "高雄市", "sitename": "B", "aqi": "120", "pollutant": "", "status": ""},
            {"county": "臺中市", "sitename": "C", "aqi": "80", "pollutant": "", "status": ""},
        ]
        results = get_all_cities_aqi(data)
        aqis = [r["aqi"] for r in results]
        assert aqis == sorted(aqis, reverse=True)

    def test_includes_city_en(self):
        """每筆結果含 city_en 欄位"""
        data = [{"county": "臺北市", "sitename": "A", "aqi": "50", "pollutant": "", "status": ""}]
        results = get_all_cities_aqi(data)
        assert len(results) >= 1
        assert results[0]["city_en"] == "Taipei"

    def test_empty_data(self):
        """空資料 → 空列表"""
        assert get_all_cities_aqi([]) == []
