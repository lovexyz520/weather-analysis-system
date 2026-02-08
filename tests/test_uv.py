"""
UV 指數分級測試 - get_uv_level
"""
import pytest
from weather_analysis.weather_api import get_uv_level


class TestGetUvLevel:
    """UV Index 5 級分類測試"""

    @pytest.mark.parametrize("uvi,expected_key,expected_color", [
        (0, "uv.level_low", "#00e400"),
        (1, "uv.level_low", "#00e400"),
        (2, "uv.level_low", "#00e400"),
        (2.5, "uv.level_moderate", "#ffff00"),
        (3, "uv.level_moderate", "#ffff00"),
        (5, "uv.level_moderate", "#ffff00"),
        (5.5, "uv.level_high", "#ff7e00"),
        (6, "uv.level_high", "#ff7e00"),
        (7, "uv.level_high", "#ff7e00"),
        (7.5, "uv.level_very_high", "#ff0000"),
        (8, "uv.level_very_high", "#ff0000"),
        (10, "uv.level_very_high", "#ff0000"),
        (10.5, "uv.level_extreme", "#8f3f97"),
        (11, "uv.level_extreme", "#8f3f97"),
        (15, "uv.level_extreme", "#8f3f97"),
    ])
    def test_uv_levels(self, uvi, expected_key, expected_color):
        key, color = get_uv_level(uvi)
        assert key == expected_key
        assert color == expected_color

    def test_boundary_2(self):
        """UVI=2 是 low, UVI=2.01 是 moderate"""
        assert get_uv_level(2)[0] == "uv.level_low"
        assert get_uv_level(2.01)[0] == "uv.level_moderate"

    def test_boundary_5(self):
        """UVI=5 是 moderate, UVI=5.01 是 high"""
        assert get_uv_level(5)[0] == "uv.level_moderate"
        assert get_uv_level(5.01)[0] == "uv.level_high"

    def test_boundary_7(self):
        """UVI=7 是 high, UVI=7.01 是 very_high"""
        assert get_uv_level(7)[0] == "uv.level_high"
        assert get_uv_level(7.01)[0] == "uv.level_very_high"

    def test_boundary_10(self):
        """UVI=10 是 very_high, UVI=10.01 是 extreme"""
        assert get_uv_level(10)[0] == "uv.level_very_high"
        assert get_uv_level(10.01)[0] == "uv.level_extreme"

    def test_zero(self):
        """UVI=0 → low"""
        assert get_uv_level(0)[0] == "uv.level_low"

    def test_returns_tuple(self):
        """回傳值為 (str, str) tuple"""
        result = get_uv_level(5)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)
