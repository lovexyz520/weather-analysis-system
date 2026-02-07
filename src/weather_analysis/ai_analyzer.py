"""
AI智慧分析模組 - 使用OpenAI GPT進行天氣智慧分析，無Key時使用規則引擎
"""
from openai import OpenAI
from weather_analysis import config
from weather_analysis.i18n import t, weekday_name


class WeatherAIAnalyzer:
    """天氣AI分析器類別"""

    def __init__(self, api_key=None):
        self.api_key = api_key or ""
        self.model = config.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def _has_openai(self):
        """檢查是否有可用的 OpenAI client"""
        return self.client is not None

    # ──────────────────────────────────────────────
    #  GPT 分析（原有邏輯）
    # ──────────────────────────────────────────────

    def analyze_weather(self, current_weather, daily_summary):
        """GPT 天氣分析"""
        weather_summary = self._prepare_weather_summary(current_weather, daily_summary)
        prompt = t("ai.gpt_prompt_weather", city=current_weather['city_tw'], summary=weather_summary)
        system_msg = t("ai.gpt_system_weather")
        return self._call_openai(system_msg, prompt)

    def suggest_activities(self, current_weather, daily_summary):
        """GPT 活動建議"""
        weather_summary = self._prepare_weather_summary(current_weather, daily_summary)
        prompt = t("ai.gpt_prompt_activities", city=current_weather['city_tw'], summary=weather_summary)
        system_msg = t("ai.gpt_system_activities")
        return self._call_openai(system_msg, prompt, temperature=0.8)

    def suggest_outfit(self, current_weather, daily_summary):
        """GPT 穿搭建議"""
        weather_summary = self._prepare_weather_summary(current_weather, daily_summary)
        prompt = t("ai.gpt_prompt_outfit", city=current_weather['city_tw'], summary=weather_summary)
        system_msg = t("ai.gpt_system_outfit")
        return self._call_openai(system_msg, prompt)

    def health_advice(self, current_weather, daily_summary):
        """GPT 健康建議"""
        weather_summary = self._prepare_weather_summary(current_weather, daily_summary)
        prompt = t("ai.gpt_prompt_health", city=current_weather['city_tw'], summary=weather_summary)
        system_msg = t("ai.gpt_system_health")
        return self._call_openai(system_msg, prompt)

    def _call_openai(self, system_msg, user_msg, temperature=0.7):
        """統一的 OpenAI API 呼叫"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=config.AI_MAX_TOKENS,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            return t("ai.error", e=str(e))

    # ──────────────────────────────────────────────
    #  規則引擎 Fallback（無 OpenAI Key 時使用）
    # ──────────────────────────────────────────────

    def get_fallback_analysis(self, current_weather, daily_summary):
        """無 OpenAI Key 時的規則引擎基礎分析"""
        temp = current_weather["temperature"]
        feels = current_weather["feels_like"]
        humidity = current_weather["humidity"]
        wind = current_weather["wind_speed"]
        weather_desc = current_weather["weather"]

        future_temps_max = [d["temp_max"] for d in daily_summary[:5]]
        future_temps_min = [d["temp_min"] for d in daily_summary[:5]]
        future_pops = [d["pop_max"] for d in daily_summary[:5]]
        future_winds = [d["wind_speed_avg"] for d in daily_summary[:5]]

        return {
            "weather_analysis": self._rule_weather_analysis(
                temp, feels, humidity, wind, weather_desc,
                daily_summary, future_temps_max, future_temps_min, future_pops,
            ),
            "activities": self._rule_activities(temp, humidity, wind, future_pops),
            "outfit": self._rule_outfit(temp, feels, humidity, future_pops, future_temps_min),
            "health": self._rule_health(temp, feels, humidity, wind, future_pops),
            "mode": "fallback",
        }

    def _rule_weather_analysis(
        self, temp, feels, humidity, wind, weather_desc,
        daily_summary, temps_max, temps_min, pops,
    ):
        """規則引擎 - 天氣分析"""
        lines = []

        # 今日總結
        lines.append(t("rule.today_summary_title"))
        lines.append(t("rule.today_summary", temp=temp, feels=feels, desc=weather_desc,
                        humidity=humidity, wind=wind))

        # 溫度警告
        if temp > 35:
            lines.append(t("rule.high_temp_warn"))
        elif temp > 30:
            lines.append(t("rule.hot"))
        elif temp < 10:
            lines.append(t("rule.low_temp_warn"))
        elif temp < 15:
            lines.append(t("rule.cool"))
        else:
            lines.append(t("rule.comfortable"))

        # 濕度
        if humidity > 80:
            lines.append(t("rule.high_humidity"))
        elif humidity < 30:
            lines.append(t("rule.low_humidity"))

        # 風速
        if wind > 10:
            lines.append(t("rule.strong_wind"))
        elif wind > 5:
            lines.append(t("rule.breeze"))

        # 未來趨勢
        lines.append(t("rule.trend_title"))
        trend_max = temps_max[-1] - temps_max[0] if len(temps_max) > 1 else 0
        if trend_max > 3:
            lines.append(t("rule.trend_warming"))
        elif trend_max < -3:
            lines.append(t("rule.trend_cooling"))
        else:
            lines.append(t("rule.trend_stable"))

        # 降雨趨勢
        rainy_days = sum(1 for p in pops if p > 60)
        if rainy_days >= 3:
            lines.append(t("rule.rain_many", n=rainy_days))
        elif rainy_days >= 1:
            lines.append(t("rule.rain_some", n=rainy_days))
        else:
            lines.append(t("rule.rain_none"))

        # 每日概覽
        lines.append(t("rule.daily_overview_title"))
        for day in daily_summary[:5]:
            wd = weekday_name(day["date"].weekday())
            pop_icon = "🌧️" if day["pop_max"] > 60 else "🌂" if day["pop_max"] > 30 else "☀️"
            lines.append(t("rule.daily_overview_row",
                           date=day['date'].strftime('%m/%d'), weekday=wd,
                           tmin=day['temp_min'], tmax=day['temp_max'],
                           pop=int(day['pop_max']), icon=pop_icon,
                           weather=day['weather']))

        return "".join(lines)

    def _rule_activities(self, temp, humidity, wind, pops):
        """規則引擎 - 活動建議"""
        lines = []
        today_pop = pops[0] if pops else 0

        lines.append(t("rule.act_title"))

        outdoor_ok = temp >= 15 and temp <= 33 and today_pop < 60 and wind < 10

        if outdoor_ok:
            lines.append(t("rule.act_outdoor_ok"))
            if temp >= 25:
                lines.append(t("rule.act_swim"))
                lines.append(t("rule.act_evening_walk"))
            else:
                lines.append(t("rule.act_cycling"))
                lines.append(t("rule.act_hiking"))
            if humidity < 70:
                lines.append(t("rule.act_photo"))
        else:
            lines.append(t("rule.act_outdoor_no"))
            reasons = []
            if temp > 33:
                reasons.append(t("rule.act_reason_hot"))
            if temp < 15:
                reasons.append(t("rule.act_reason_cold"))
            if today_pop >= 60:
                reasons.append(t("rule.act_reason_rain"))
            if wind >= 10:
                reasons.append(t("rule.act_reason_wind"))
            if reasons:
                joiner = {"zh_tw": "\u3001", "en": ", "}
                from weather_analysis.i18n import get_lang
                sep = joiner.get(get_lang(), ", ")
                lines.append(t("rule.act_reason_prefix", reasons=sep.join(reasons)))

            lines.append(t("rule.act_indoor_movie"))
            lines.append(t("rule.act_indoor_gym"))
            lines.append(t("rule.act_indoor_cafe"))

        # 運動建議
        lines.append(t("rule.act_exercise_title"))
        if temp > 30:
            lines.append(t("rule.act_exercise_hot"))
        elif temp < 10:
            lines.append(t("rule.act_exercise_cold"))
        else:
            lines.append(t("rule.act_exercise_normal"))

        return "".join(lines)

    def _rule_outfit(self, temp, feels, humidity, pops, temps_min):
        """規則引擎 - 穿搭建議"""
        lines = []
        today_pop = pops[0] if pops else 0

        lines.append(t("rule.outfit_title"))

        # 依溫度區間建議
        if temp > 30:
            lines.append(t("rule.outfit_hot_top"))
            lines.append(t("rule.outfit_hot_bottom"))
            lines.append(t("rule.outfit_hot_acc"))
        elif temp > 25:
            lines.append(t("rule.outfit_warm_top"))
            lines.append(t("rule.outfit_warm_bottom"))
            lines.append(t("rule.outfit_warm_jacket"))
        elif temp > 20:
            lines.append(t("rule.outfit_mild_top"))
            lines.append(t("rule.outfit_mild_bottom"))
            lines.append(t("rule.outfit_mild_jacket"))
        elif temp > 15:
            lines.append(t("rule.outfit_cool_top"))
            lines.append(t("rule.outfit_cool_bottom"))
            lines.append(t("rule.outfit_cool_jacket"))
            lines.append(t("rule.outfit_cool_acc"))
        else:
            lines.append(t("rule.outfit_cold_top"))
            lines.append(t("rule.outfit_cold_bottom"))
            lines.append(t("rule.outfit_cold_jacket"))
            lines.append(t("rule.outfit_cold_acc"))

        # 降雨提醒
        if today_pop > 60:
            lines.append(t("rule.outfit_rain_must"))
        elif today_pop > 30:
            lines.append(t("rule.outfit_rain_maybe"))

        # 濕度提醒
        if humidity > 80:
            lines.append(t("rule.outfit_humid"))

        # 未來趨勢
        lines.append(t("rule.outfit_future_title"))
        min_temp_future = min(temps_min) if temps_min else temp
        max_pop_future = max(pops) if pops else 0

        if min_temp_future < temp - 5:
            lines.append(t("rule.outfit_future_colder"))
        elif min_temp_future > temp + 5:
            lines.append(t("rule.outfit_future_warmer"))
        else:
            lines.append(t("rule.outfit_future_stable"))

        if max_pop_future > 60:
            lines.append(t("rule.outfit_future_rain"))

        return "".join(lines)

    def _rule_health(self, temp, feels, humidity, wind, pops):
        """規則引擎 - 健康建議"""
        lines = []

        lines.append(t("rule.health_title"))

        # 高溫
        if temp > 33:
            lines.append(t("rule.health_heatstroke"))
        elif temp > 28:
            lines.append(t("rule.health_warm"))

        # 低溫
        if temp < 10:
            lines.append(t("rule.health_cold_warn"))
        elif temp < 15:
            lines.append(t("rule.health_cool"))

        # 濕度
        if humidity > 80:
            lines.append(t("rule.health_humid"))
        elif humidity < 30:
            lines.append(t("rule.health_dry"))

        # 風速
        if wind > 10:
            lines.append(t("rule.health_wind"))

        # 運動時間建議
        lines.append(t("rule.health_exercise_title"))
        if temp > 30:
            lines.append(t("rule.health_exercise_hot"))
        elif temp < 10:
            lines.append(t("rule.health_exercise_cold"))
        else:
            lines.append(t("rule.health_exercise_normal"))

        # 飲食建議
        lines.append(t("rule.health_diet_title"))
        if temp > 30:
            lines.append(t("rule.health_diet_hot"))
        elif temp < 15:
            lines.append(t("rule.health_diet_cold"))
        else:
            lines.append(t("rule.health_diet_normal"))

        # 特殊族群提醒
        lines.append(t("rule.health_special_title"))
        if temp > 33 or temp < 10:
            lines.append(t("rule.health_elderly"))
            lines.append(t("rule.health_children"))
        if humidity > 70:
            lines.append(t("rule.health_allergy"))

        today_pop = pops[0] if pops else 0
        if today_pop > 60:
            lines.append(t("rule.health_asthma"))

        return "".join(lines)

    # ──────────────────────────────────────────────
    #  綜合分析入口
    # ──────────────────────────────────────────────

    def comprehensive_analysis(self, current_weather, daily_summary):
        """
        綜合智慧分析（包含所有分析項目）

        有 OpenAI Key → GPT 深度分析（失敗時 fallback）
        無 OpenAI Key → 規則引擎基礎分析
        """
        if not self._has_openai():
            return self.get_fallback_analysis(current_weather, daily_summary)

        # 嘗試 GPT 分析
        try:
            result = {
                "weather_analysis": self.analyze_weather(current_weather, daily_summary),
                "activities": self.suggest_activities(current_weather, daily_summary),
                "outfit": self.suggest_outfit(current_weather, daily_summary),
                "health": self.health_advice(current_weather, daily_summary),
                "mode": "gpt",
            }
            # 檢查是否所有回應都包含錯誤訊息（全部失敗時 fallback）
            error_prefix_zh = "AI分析時發生錯誤"
            error_prefix_en = "AI analysis error"
            error_count = sum(
                1 for v in result.values()
                if isinstance(v, str) and (v.startswith(error_prefix_zh) or v.startswith(error_prefix_en))
            )
            if error_count >= 4:
                fallback = self.get_fallback_analysis(current_weather, daily_summary)
                fallback["weather_analysis"] = (
                    "⚠️ " + t("ai.gpt_failed_fallback") + "\n\n"
                    + fallback["weather_analysis"]
                )
                return fallback
            return result
        except Exception:
            return self.get_fallback_analysis(current_weather, daily_summary)

    def _prepare_weather_summary(self, current_weather, daily_summary):
        """準備天氣資料摘要"""
        summary = f"""
{t("ai.summary_current")}
- {t("ai.summary_temp")}: {current_weather['temperature']}°C ({t("ai.summary_feels")} {current_weather['feels_like']}°C)
- {t("ai.summary_humidity")}: {current_weather['humidity']}%
- {t("ai.summary_wind")}: {current_weather['wind_speed']} m/s
- {t("ai.summary_condition")}: {current_weather['weather']}

{t("ai.summary_forecast")}
"""
        for day in daily_summary[:5]:
            wd = weekday_name(day['date'].weekday())
            summary += f"""
- {day['date'].strftime('%m/%d')} ({wd}):
  {t("ai.summary_temp_range")} {day['temp_min']}°C ~ {day['temp_max']}°C
  {t("ai.summary_rain")} {int(day['pop_max'])}%
  {day['weather']}
"""
        return summary
