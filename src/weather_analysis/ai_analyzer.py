"""
AI智慧分析模組 - 使用OpenAI GPT進行天氣智慧分析，無Key時使用規則引擎
"""
from openai import OpenAI
from weather_analysis import config


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
        prompt = f"""你是一位專業的氣象分析師，請根據以下台灣{current_weather['city_tw']}的天氣資料，提供詳細的天氣分析：

{weather_summary}

請提供：
1. 今日天氣總結（2-3句話）
2. 未來天氣趨勢分析
3. 需要特別注意的天氣變化

請用專業但易懂的方式說明，並使用繁體中文。"""

        return self._call_openai(
            "你是一位專業的台灣氣象分析師，擅長解析天氣數據並提供實用建議。",
            prompt,
        )

    def suggest_activities(self, current_weather, daily_summary):
        """GPT 活動建議"""
        weather_summary = self._prepare_weather_summary(current_weather, daily_summary)
        prompt = f"""根據{current_weather['city_tw']}的天氣狀況：

{weather_summary}

請針對今天和未來幾天，推薦5個適合的活動或建議：
- 戶外活動（如果天氣適合）
- 室內活動（如果天氣不佳）
- 運動建議
- 出遊建議
- 日常生活建議

每個建議請說明原因，使用繁體中文，以列表方式呈現。"""

        return self._call_openai(
            "你是一位生活顧問，擅長根據天氣提供實用的活動建議。",
            prompt,
            temperature=0.8,
        )

    def suggest_outfit(self, current_weather, daily_summary):
        """GPT 穿搭建議"""
        weather_summary = self._prepare_weather_summary(current_weather, daily_summary)
        prompt = f"""根據{current_weather['city_tw']}的天氣：

{weather_summary}

請提供今日和未來幾天的穿搭建議：
1. 今日穿搭建議（上衣、下著、外套、配件）
2. 未來3天的穿搭趨勢
3. 特殊提醒（例如：需要帶傘、防曬等）

請考慮溫度、濕度、降雨機率等因素，使用繁體中文。"""

        return self._call_openai(
            "你是一位時尚顧問，擅長根據天氣提供實用的穿搭建議。",
            prompt,
        )

    def health_advice(self, current_weather, daily_summary):
        """GPT 健康建議"""
        weather_summary = self._prepare_weather_summary(current_weather, daily_summary)
        prompt = f"""根據{current_weather['city_tw']}的天氣狀況：

{weather_summary}

請提供健康相關建議：
1. 今日健康注意事項
2. 運動時間建議
3. 飲食建議（冷飲/熱飲、補水等）
4. 特殊族群提醒（老人、小孩、過敏體質）
5. 未來幾天的健康準備

請用專業但易懂的方式說明，使用繁體中文。"""

        return self._call_openai(
            "你是一位健康顧問，擅長根據天氣提供健康建議。",
            prompt,
        )

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
            return f"AI分析時發生錯誤: {str(e)}"

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

        # 取得未來幾天的資料
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
        lines.append("**📋 今日天氣總結**\n")
        lines.append(f"目前氣溫 {temp}°C（體感 {feels}°C），{weather_desc}，"
                      f"濕度 {humidity}%，風速 {wind} m/s。\n")

        # 溫度警告
        if temp > 35:
            lines.append("- ⚠️ **高溫警告**：氣溫超過 35°C，請避免長時間曝曬，注意防曬補水。\n")
        elif temp > 30:
            lines.append("- 🌡️ 天氣炎熱，建議多補充水分。\n")
        elif temp < 10:
            lines.append("- ⚠️ **低溫警告**：氣溫低於 10°C，注意保暖，穿著多層衣物。\n")
        elif temp < 15:
            lines.append("- 🧣 天氣偏涼，建議攜帶外套。\n")
        else:
            lines.append("- ✅ 氣溫舒適宜人。\n")

        # 濕度
        if humidity > 80:
            lines.append("- 💧 濕度偏高（>80%），體感悶熱，建議待在通風處。\n")
        elif humidity < 30:
            lines.append("- 🏜️ 濕度偏低，注意皮膚保濕。\n")

        # 風速
        if wind > 10:
            lines.append("- 💨 風速較大（>10 m/s），外出注意安全，避免山區活動。\n")
        elif wind > 5:
            lines.append("- 🍃 微風吹拂，體感較涼爽。\n")

        # 未來趨勢
        lines.append("\n**📈 未來天氣趨勢**\n")
        trend_max = temps_max[-1] - temps_max[0] if len(temps_max) > 1 else 0
        if trend_max > 3:
            lines.append("- 未來幾天氣溫**逐漸升高**，請注意防暑。\n")
        elif trend_max < -3:
            lines.append("- 未來幾天氣溫**逐漸下降**，請注意保暖。\n")
        else:
            lines.append("- 未來幾天氣溫**相對穩定**。\n")

        # 降雨趨勢
        rainy_days = sum(1 for p in pops if p > 60)
        if rainy_days >= 3:
            lines.append(f"- 🌧️ 未來 5 天中有 {rainy_days} 天降雨機率偏高，建議備好雨具。\n")
        elif rainy_days >= 1:
            lines.append(f"- 🌂 部分天數有降雨可能（{rainy_days} 天），出門可攜帶雨傘。\n")
        else:
            lines.append("- ☀️ 未來幾天降雨機率不高，天氣大致晴朗。\n")

        # 每日概覽
        lines.append("\n**📅 每日概覽**\n")
        for day in daily_summary[:5]:
            weekday = ["一", "二", "三", "四", "五", "六", "日"][day["date"].weekday()]
            pop_icon = "🌧️" if day["pop_max"] > 60 else "🌂" if day["pop_max"] > 30 else "☀️"
            lines.append(
                f"- {day['date'].strftime('%m/%d')}（{weekday}）："
                f"{day['temp_min']}°C ~ {day['temp_max']}°C，"
                f"降雨 {int(day['pop_max'])}% {pop_icon}，{day['weather']}\n"
            )

        return "".join(lines)

    def _rule_activities(self, temp, humidity, wind, pops):
        """規則引擎 - 活動建議"""
        lines = []
        today_pop = pops[0] if pops else 0

        lines.append("**🎯 今日活動建議**\n\n")

        # 判斷是否適合戶外
        outdoor_ok = temp >= 15 and temp <= 33 and today_pop < 60 and wind < 10

        if outdoor_ok:
            lines.append("✅ 今天天氣適合戶外活動！\n\n")
            if temp >= 25:
                lines.append("- 🏊 **水上活動**：天氣炎熱，適合游泳、玩水消暑。\n")
                lines.append("- 🌅 **傍晚散步**：避開正午高溫，建議傍晚時分到公園散步。\n")
            else:
                lines.append("- 🚴 **自行車騎行**：氣溫舒適，適合戶外騎行運動。\n")
                lines.append("- 🥾 **健行登山**：天氣涼爽，適合步道健行。\n")

            if humidity < 70:
                lines.append("- 📸 **戶外攝影**：濕度適中，適合外出拍照。\n")
        else:
            lines.append("⚠️ 今天較不適合長時間戶外活動。\n\n")
            reasons = []
            if temp > 33:
                reasons.append("氣溫過高")
            if temp < 15:
                reasons.append("氣溫偏低")
            if today_pop >= 60:
                reasons.append("降雨機率高")
            if wind >= 10:
                reasons.append("風速過大")
            if reasons:
                lines.append(f"- 原因：{'、'.join(reasons)}\n")

            lines.append("- 🎬 **室內活動**：建議看電影、逛書店、參觀展覽。\n")
            lines.append("- 🏋️ **室內運動**：可到健身房、室內游泳池運動。\n")
            lines.append("- ☕ **咖啡廳休閒**：找間舒適的咖啡廳，享受悠閒時光。\n")

        # 運動建議
        lines.append("\n**🏃 運動建議**\n\n")
        if temp > 30:
            lines.append("- 建議在清晨（6-8時）或傍晚（17-19時）運動，避開高溫時段。\n")
        elif temp < 10:
            lines.append("- 運動前務必做好暖身，避免肌肉拉傷。\n")
        else:
            lines.append("- 氣溫適中，適合全天運動，記得補充水分。\n")

        return "".join(lines)

    def _rule_outfit(self, temp, feels, humidity, pops, temps_min):
        """規則引擎 - 穿搭建議"""
        lines = []
        today_pop = pops[0] if pops else 0

        lines.append("**👔 今日穿搭建議**\n\n")

        # 依溫度區間建議
        if temp > 30:
            lines.append("- 👕 **上衣**：短袖、透氣材質（棉、麻），淺色系較佳。\n")
            lines.append("- 👖 **下著**：短褲、薄長褲或裙裝。\n")
            lines.append("- 🧢 **配件**：太陽眼鏡、遮陽帽、防曬乳。\n")
        elif temp > 25:
            lines.append("- 👕 **上衣**：短袖或薄長袖 T-shirt。\n")
            lines.append("- 👖 **下著**：長褲或短褲皆可。\n")
            lines.append("- 🧥 **外套**：室內冷氣房可備薄外套。\n")
        elif temp > 20:
            lines.append("- 👕 **上衣**：長袖上衣、薄毛衣。\n")
            lines.append("- 👖 **下著**：長褲為主。\n")
            lines.append("- 🧥 **外套**：薄外套或針織衫。\n")
        elif temp > 15:
            lines.append("- 👕 **上衣**：長袖上衣 + 毛衣。\n")
            lines.append("- 👖 **下著**：長褲、牛仔褲。\n")
            lines.append("- 🧥 **外套**：風衣、夾克或厚外套。\n")
            lines.append("- 🧣 **配件**：圍巾備用。\n")
        else:
            lines.append("- 👕 **上衣**：多層穿搭 — 內搭 + 毛衣 + 外套。\n")
            lines.append("- 👖 **下著**：厚長褲，可考慮內搭褲。\n")
            lines.append("- 🧥 **外套**：厚外套、羽絨衣。\n")
            lines.append("- 🧣 **配件**：圍巾、手套、毛帽。\n")

        # 降雨提醒
        if today_pop > 60:
            lines.append("\n- 🌂 **必備雨具**：降雨機率高，請攜帶雨傘或穿防水外套。\n")
        elif today_pop > 30:
            lines.append("\n- 🌂 **建議帶傘**：有降雨可能，建議備用雨傘。\n")

        # 濕度提醒
        if humidity > 80:
            lines.append("- 💧 濕度高，衣物建議選擇吸濕排汗材質。\n")

        # 未來趨勢
        lines.append("\n**📅 未來穿搭趨勢**\n\n")
        min_temp_future = min(temps_min) if temps_min else temp
        max_pop_future = max(pops) if pops else 0

        if min_temp_future < temp - 5:
            lines.append("- 未來幾天氣溫將明顯下降，請準備較厚的衣物。\n")
        elif min_temp_future > temp + 5:
            lines.append("- 未來幾天氣溫將上升，可準備較輕便的穿著。\n")
        else:
            lines.append("- 未來幾天氣溫變化不大，穿搭可維持今日風格。\n")

        if max_pop_future > 60:
            lines.append("- 未來幾天有降雨可能，建議隨身攜帶雨具。\n")

        return "".join(lines)

    def _rule_health(self, temp, feels, humidity, wind, pops):
        """規則引擎 - 健康建議"""
        lines = []

        lines.append("**💪 今日健康注意事項**\n\n")

        # 高溫
        if temp > 33:
            lines.append("- ⚠️ **中暑風險**：高溫環境下請注意以下事項：\n")
            lines.append("  - 每小時至少補充 250ml 水分\n")
            lines.append("  - 避免 10:00-15:00 曝曬\n")
            lines.append("  - 出現頭暈、噁心請立即至陰涼處休息\n")
        elif temp > 28:
            lines.append("- 🌡️ 天氣偏熱，注意補充水分，建議每日飲水 2000ml 以上。\n")

        # 低溫
        if temp < 10:
            lines.append("- ⚠️ **低溫注意**：\n")
            lines.append("  - 心血管疾病患者注意保暖\n")
            lines.append("  - 避免突然激烈運動\n")
            lines.append("  - 起床時先在被窩暖身再起身\n")
        elif temp < 15:
            lines.append("- 🧣 天氣偏涼，出門注意保暖，預防感冒。\n")

        # 濕度
        if humidity > 80:
            lines.append("- 💧 **高濕警示**：濕度偏高可能加重過敏症狀。\n")
            lines.append("  - 過敏體質者建議使用除濕機\n")
            lines.append("  - 注意食物保鮮，避免細菌滋生\n")
        elif humidity < 30:
            lines.append("- 🏜️ 空氣乾燥，注意皮膚保濕、多喝水，可使用加濕器。\n")

        # 風速
        if wind > 10:
            lines.append("- 💨 風大注意：外出時注意眼睛防護，配戴口罩防風沙。\n")

        # 運動時間建議
        lines.append("\n**🏃 運動時間建議**\n\n")
        if temp > 30:
            lines.append("- ⏰ 最佳運動時段：清晨 06:00-08:00 或傍晚 17:00-19:00\n")
            lines.append("- 避免正午時段戶外運動\n")
        elif temp < 10:
            lines.append("- ⏰ 最佳運動時段：上午 10:00-12:00（氣溫回升後）\n")
            lines.append("- 運動前充分暖身 10-15 分鐘\n")
        else:
            lines.append("- ⏰ 全天皆適合運動，記得做好暖身與收操。\n")

        # 飲食建議
        lines.append("\n**🍽️ 飲食建議**\n\n")
        if temp > 30:
            lines.append("- 多喝水、少量多次補充電解質\n")
            lines.append("- 可飲用綠豆湯、仙草等消暑飲品\n")
            lines.append("- 避免過多冰品，以免腸胃不適\n")
        elif temp < 15:
            lines.append("- 適合喝熱湯、薑茶等暖身飲品\n")
            lines.append("- 多攝取富含維生素C的食物增強免疫力\n")
        else:
            lines.append("- 氣溫適中，均衡飲食即可，每日建議飲水 1500-2000ml。\n")

        # 特殊族群提醒
        lines.append("\n**👴👶 特殊族群提醒**\n\n")
        if temp > 33 or temp < 10:
            lines.append("- **長者**：注意室內外溫差，進出冷氣房時緩步適應。\n")
            lines.append("- **幼童**：注意體溫調節，適時增減衣物。\n")
        if humidity > 70:
            lines.append("- **過敏體質**：高濕環境容易誘發過敏，建議保持居家乾燥通風。\n")

        today_pop = pops[0] if pops else 0
        if today_pop > 60:
            lines.append("- **氣喘患者**：降雨前後氣壓變化大，注意攜帶藥物。\n")

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
            error_count = sum(
                1 for v in result.values()
                if isinstance(v, str) and v.startswith("AI分析時發生錯誤")
            )
            if error_count >= 4:
                fallback = self.get_fallback_analysis(current_weather, daily_summary)
                fallback["weather_analysis"] = (
                    "⚠️ GPT 分析失敗，已切換為基礎規則分析。\n\n"
                    + fallback["weather_analysis"]
                )
                return fallback
            return result
        except Exception:
            return self.get_fallback_analysis(current_weather, daily_summary)

    def _prepare_weather_summary(self, current_weather, daily_summary):
        """準備天氣資料摘要"""
        summary = f"""
【即時天氣】
- 溫度: {current_weather['temperature']}°C (體感 {current_weather['feels_like']}°C)
- 濕度: {current_weather['humidity']}%
- 風速: {current_weather['wind_speed']} m/s
- 天氣狀況: {current_weather['weather']}

【未來5天預報】
"""
        for day in daily_summary[:5]:
            summary += f"""
- {day['date'].strftime('%m/%d')} ({['一','二','三','四','五','六','日'][day['date'].weekday()]}):
  溫度 {day['temp_min']}°C ~ {day['temp_max']}°C
  降雨機率 {int(day['pop_max'])}%
  {day['weather']}
"""
        return summary
