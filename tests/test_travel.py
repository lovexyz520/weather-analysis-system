"""
旅遊推薦模組測試 - travel.score_day, recommend_best_days
"""
import pytest
from datetime import date
from weather_analysis.travel import score_day, recommend_best_days, _build_reasons


# ── score_day ──


class TestScoreDay:
    """score_day 評分邏輯測試"""

    def test_perfect_day(self):
        """最佳天氣 → 接近滿分"""
        day = {"temp_avg": 22, "pop_max": 0, "wind_speed_avg": 3, "humidity_avg": 55}
        result = score_day(day)
        assert result["total"] == 100
        assert result["temp_score"] == 40
        assert result["rain_score"] == 25
        assert result["wind_score"] == 15
        assert result["humidity_score"] == 20

    def test_temp_range_boundary_low(self):
        """溫度 18°C 仍在滿分區間"""
        day = {"temp_avg": 18, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 55}
        assert score_day(day)["temp_score"] == 40

    def test_temp_range_boundary_high(self):
        """溫度 26°C 仍在滿分區間"""
        day = {"temp_avg": 26, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 55}
        assert score_day(day)["temp_score"] == 40

    def test_temp_below_comfort(self):
        """溫度低於舒適區 → 扣分"""
        day = {"temp_avg": 15, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 55}
        result = score_day(day)
        # 偏離 3 度, 每度扣 3 分 → 40 - 9 = 31
        assert result["temp_score"] == 31

    def test_temp_above_comfort(self):
        """溫度高於舒適區 → 扣分"""
        day = {"temp_avg": 30, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 55}
        result = score_day(day)
        # 偏離 4 度, 每度扣 3 分 → 40 - 12 = 28
        assert result["temp_score"] == 28

    def test_temp_extreme_hot(self):
        """極端高溫 → 溫度分歸零"""
        day = {"temp_avg": 40, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 55}
        result = score_day(day)
        # 偏離 14 度, 14*3=42 > 40 → max(0, ...) = 0
        assert result["temp_score"] == 0

    def test_rain_full(self):
        """100% 降雨 → 降雨分歸零"""
        day = {"temp_avg": 22, "pop_max": 100, "wind_speed_avg": 0, "humidity_avg": 55}
        result = score_day(day)
        assert result["rain_score"] == 0

    def test_rain_partial(self):
        """50% 降雨 → 部分扣分"""
        day = {"temp_avg": 22, "pop_max": 50, "wind_speed_avg": 0, "humidity_avg": 55}
        result = score_day(day)
        # 25 - 50/10 * 2.5 = 25 - 12.5 = 12.5
        assert result["rain_score"] == 12.5

    def test_wind_calm(self):
        """風速 <= 5 滿分"""
        day = {"temp_avg": 22, "pop_max": 0, "wind_speed_avg": 5, "humidity_avg": 55}
        assert score_day(day)["wind_score"] == 15

    def test_wind_strong(self):
        """風速 > 5 → 扣分"""
        day = {"temp_avg": 22, "pop_max": 0, "wind_speed_avg": 8, "humidity_avg": 55}
        result = score_day(day)
        # 15 - (8-5)*3 = 15 - 9 = 6
        assert result["wind_score"] == 6

    def test_wind_extreme(self):
        """極端風速 → 風速分歸零"""
        day = {"temp_avg": 22, "pop_max": 0, "wind_speed_avg": 15, "humidity_avg": 55}
        result = score_day(day)
        # 15 - (15-5)*3 = 15 - 30 → max(0, -15) = 0
        assert result["wind_score"] == 0

    def test_humidity_comfort_zone(self):
        """濕度 40-70% 滿分"""
        for h in [40, 55, 70]:
            day = {"temp_avg": 22, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": h}
            assert score_day(day)["humidity_score"] == 20

    def test_humidity_too_dry(self):
        """濕度過低 → 扣分"""
        day = {"temp_avg": 22, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 25}
        result = score_day(day)
        # diff=15, 20 - 15/5*2 = 20 - 6 = 14
        assert result["humidity_score"] == 14

    def test_humidity_too_wet(self):
        """濕度過高 → 扣分"""
        day = {"temp_avg": 22, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 85}
        result = score_day(day)
        # diff=15, 20 - 15/5*2 = 20 - 6 = 14
        assert result["humidity_score"] == 14

    def test_bad_day(self):
        """惡劣天氣 → 極低分"""
        day = {"temp_avg": 38, "pop_max": 90, "wind_speed_avg": 12, "humidity_avg": 95}
        result = score_day(day)
        assert result["total"] < 25

    def test_defaults(self):
        """空 dict → 使用預設值不報錯"""
        result = score_day({})
        assert 0 <= result["total"] <= 100

    def test_total_is_sum(self):
        """total == 四維度之和"""
        day = {"temp_avg": 20, "pop_max": 30, "wind_speed_avg": 6, "humidity_avg": 50}
        result = score_day(day)
        expected = result["temp_score"] + result["rain_score"] + result["wind_score"] + result["humidity_score"]
        assert result["total"] == round(expected, 1)


# ── _build_reasons ──


class TestBuildReasons:
    """_build_reasons 原因判斷測試"""

    def test_all_good(self):
        """全部指標良好 → 正面原因"""
        day = {"temp_avg": 22, "pop_max": 10, "wind_speed_avg": 3, "humidity_avg": 55}
        scores = score_day(day)
        reasons = _build_reasons(day, scores)
        assert "travel.reason_temp_good" in reasons
        assert "travel.reason_rain_low" in reasons
        assert "travel.reason_wind_calm" in reasons
        assert "travel.reason_humidity_good" in reasons

    def test_hot_day(self):
        """高溫 → reason_temp_hot"""
        day = {"temp_avg": 32, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 55}
        scores = score_day(day)
        reasons = _build_reasons(day, scores)
        assert "travel.reason_temp_hot" in reasons

    def test_cold_day(self):
        """低溫 → reason_temp_cold"""
        day = {"temp_avg": 10, "pop_max": 0, "wind_speed_avg": 0, "humidity_avg": 55}
        scores = score_day(day)
        reasons = _build_reasons(day, scores)
        assert "travel.reason_temp_cold" in reasons

    def test_rainy_day(self):
        """高降雨 → reason_rain_high"""
        day = {"temp_avg": 22, "pop_max": 70, "wind_speed_avg": 0, "humidity_avg": 55}
        scores = score_day(day)
        reasons = _build_reasons(day, scores)
        assert "travel.reason_rain_high" in reasons

    def test_windy_day(self):
        """強風 → reason_wind_strong"""
        day = {"temp_avg": 22, "pop_max": 0, "wind_speed_avg": 10, "humidity_avg": 55}
        scores = score_day(day)
        reasons = _build_reasons(day, scores)
        assert "travel.reason_wind_strong" in reasons


# ── recommend_best_days ──


class TestRecommendBestDays:
    """recommend_best_days 推薦邏輯測試"""

    def _make_days(self, temps):
        """輔助：用溫度清單產生 daily_summary"""
        return [
            {
                "date": date(2025, 1, i + 1),
                "temp_avg": t,
                "pop_max": 10,
                "wind_speed_avg": 3,
                "humidity_avg": 55,
                "weather": "晴",
                "icon": "01d",
            }
            for i, t in enumerate(temps)
        ]

    def test_empty_input(self):
        """空列表 → 空結果"""
        assert recommend_best_days([]) == []

    def test_top_two_recommended(self):
        """最佳 2 天標記為 recommended"""
        # 22°C, 30°C, 10°C → 22 最佳, 30 其次, 10 最差
        days = self._make_days([22, 30, 10])
        results = recommend_best_days(days)
        recommended = [r for r in results if r["recommended"]]
        assert len(recommended) == 2
        # 22°C 那天一定是推薦之一
        rec_temps = {r["temp_avg"] for r in recommended}
        assert 22 in rec_temps

    def test_single_day(self):
        """只有 1 天 → 標記為 recommended"""
        days = self._make_days([22])
        results = recommend_best_days(days)
        assert len(results) == 1
        assert results[0]["recommended"] is True

    def test_result_sorted_by_date(self):
        """回傳結果按日期排序"""
        days = self._make_days([30, 22, 10, 25, 5])
        results = recommend_best_days(days)
        dates = [r["date"] for r in results]
        assert dates == sorted(dates)

    def test_result_contains_required_fields(self):
        """回傳 dict 包含必要欄位"""
        days = self._make_days([22])
        result = recommend_best_days(days)[0]
        for key in ["date", "score", "scores", "reasons", "recommended", "temp_avg", "pop_max"]:
            assert key in result
