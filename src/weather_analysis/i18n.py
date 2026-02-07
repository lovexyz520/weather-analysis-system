"""
多語言支援模組 (i18n) - 繁體中文 / English
"""
import streamlit as st

SUPPORTED_LANGS = {"zh_tw": "繁體中文", "en": "English"}

TRANSLATIONS = {
    # ── app.py: 頁面層級 ──
    "app.page_title": {"zh_tw": "智慧天氣分析系統", "en": "Smart Weather Analysis"},
    "app.header": {"zh_tw": "智慧天氣分析系統", "en": "Smart Weather Analysis"},
    "app.footer": {
        "zh_tw": "智慧天氣分析系統 v1.1.0 | 資料來源: OpenWeatherMap | AI: OpenAI GPT / 規則引擎 | Made with ❤️ using Streamlit",
        "en": "Smart Weather Analysis v1.1.0 | Data: OpenWeatherMap | AI: OpenAI GPT / Rule Engine | Made with ❤️ using Streamlit",
    },
    "app.no_data_hint": {
        "zh_tw": "請在側邊欄輸入 OpenWeatherMap API Key 並點擊「更新天氣資料」",
        "en": "Please enter your OpenWeatherMap API Key in the sidebar and click 'Update Weather'",
    },
    "app.loading": {"zh_tw": "正在載入 {city} 的天氣資料...", "en": "Loading weather data for {city}..."},
    "app.data_updated": {"zh_tw": "資料更新成功！", "en": "Data updated successfully!"},
    "app.loading_weather": {"zh_tw": "正在載入天氣資料...", "en": "Loading weather data..."},
    "app.analyzing": {"zh_tw": "正在分析天氣資料中...", "en": "Analyzing weather data..."},

    # ── sidebar ──
    "sidebar.title": {"zh_tw": "系統設定", "en": "Settings"},
    "sidebar.api_key_section": {"zh_tw": "API Key 設定", "en": "API Key Settings"},
    "sidebar.owm_label": {"zh_tw": "OpenWeatherMap API Key", "en": "OpenWeatherMap API Key"},
    "sidebar.owm_placeholder": {
        "zh_tw": "輸入 API Key（或由環境變數自動載入）",
        "en": "Enter API Key (or auto-loaded from env)",
    },
    "sidebar.owm_valid": {"zh_tw": "API Key 驗證成功", "en": "API Key verified"},
    "sidebar.owm_invalid": {
        "zh_tw": "API Key 驗證失敗，請確認金鑰是否正確",
        "en": "API Key verification failed, please check your key",
    },
    "sidebar.owm_env_loaded": {
        "zh_tw": "已從環境變數載入（如需覆蓋請在上方輸入）",
        "en": "Loaded from environment variable (enter above to override)",
    },
    "sidebar.owm_not_set": {
        "zh_tw": "未偵測到環境變數，請在上方輸入 API Key",
        "en": "No environment variable detected, please enter API Key above",
    },
    "sidebar.oai_label": {"zh_tw": "OpenAI API Key（可選）", "en": "OpenAI API Key (optional)"},
    "sidebar.oai_placeholder": {
        "zh_tw": "輸入 API Key 啟用 GPT 深度分析",
        "en": "Enter API Key to enable GPT analysis",
    },
    "sidebar.oai_valid": {"zh_tw": "OpenAI Key 驗證成功 (GPT 模式)", "en": "OpenAI Key verified (GPT mode)"},
    "sidebar.oai_invalid": {
        "zh_tw": "OpenAI Key 驗證失敗，將使用基礎規則分析",
        "en": "OpenAI Key verification failed, will use rule-based analysis",
    },
    "sidebar.oai_env_loaded": {
        "zh_tw": "已從環境變數載入 (GPT 模式)",
        "en": "Loaded from env (GPT mode)",
    },
    "sidebar.oai_not_set": {
        "zh_tw": "未設定（將使用基礎規則分析）",
        "en": "Not set (will use rule-based analysis)",
    },
    "sidebar.onecall_label": {"zh_tw": "One Call API Key（可選）", "en": "One Call API Key (optional)"},
    "sidebar.onecall_placeholder": {
        "zh_tw": "輸入 One Call 3.0 API Key 啟用官方警報",
        "en": "Enter One Call 3.0 API Key for official alerts",
    },
    "sidebar.onecall_env_loaded": {
        "zh_tw": "已從環境變數載入 (官方警報)",
        "en": "Loaded from env (official alerts)",
    },
    "sidebar.onecall_not_set": {
        "zh_tw": "未設定（僅使用規則警報）",
        "en": "Not set (rule-based alerts only)",
    },
    "sidebar.city_label": {"zh_tw": "選擇城市", "en": "Select City"},
    "sidebar.update_btn": {"zh_tw": "更新天氣資料", "en": "Update Weather"},
    "sidebar.no_owm_key": {
        "zh_tw": "請先輸入 OpenWeatherMap API Key",
        "en": "Please enter OpenWeatherMap API Key first",
    },
    "sidebar.sys_info": {"zh_tw": "系統資訊", "en": "System Info"},
    "sidebar.data_source": {"zh_tw": "資料來源", "en": "Data Source"},
    "sidebar.current_city": {"zh_tw": "當前城市", "en": "Current City"},
    "sidebar.analysis_mode": {"zh_tw": "分析模式", "en": "Analysis Mode"},
    "sidebar.cache_time": {"zh_tw": "快取時間", "en": "Cache Duration"},
    "sidebar.cache_minutes": {"zh_tw": "{n} 分鐘", "en": "{n} min"},
    "sidebar.update_time": {"zh_tw": "更新時間", "en": "Updated"},
    "sidebar.ai_mode_gpt": {"zh_tw": "GPT 深度分析", "en": "GPT Deep Analysis"},
    "sidebar.ai_mode_rule": {"zh_tw": "基礎規則分析", "en": "Rule-based Analysis"},
    "sidebar.lang_label": {"zh_tw": "Language / 語言", "en": "Language / 語言"},

    # ── tabs ──
    "tab.current": {"zh_tw": "即時天氣", "en": "Current Weather"},
    "tab.charts": {"zh_tw": "預報圖表", "en": "Forecast Charts"},
    "tab.daily": {"zh_tw": "每日預報", "en": "Daily Forecast"},
    "tab.ai": {"zh_tw": "AI智慧分析", "en": "AI Analysis"},

    # ── metric ──
    "metric.temperature": {"zh_tw": "溫度", "en": "Temperature"},
    "metric.feels_like": {"zh_tw": "體感 {v}°C", "en": "Feels {v}°C"},
    "metric.humidity": {"zh_tw": "濕度", "en": "Humidity"},
    "metric.wind_speed": {"zh_tw": "風速", "en": "Wind Speed"},
    "metric.clouds": {"zh_tw": "雲量", "en": "Cloud Cover"},
    "metric.temp_max": {"zh_tw": "最高溫", "en": "High"},
    "metric.temp_min": {"zh_tw": "最低溫", "en": "Low"},
    "metric.pressure": {"zh_tw": "氣壓", "en": "Pressure"},
    "metric.sunrise": {"zh_tw": "日出", "en": "Sunrise"},
    "metric.sunset": {"zh_tw": "日落", "en": "Sunset"},
    "metric.data_time": {"zh_tw": "資料時間", "en": "Data Time"},
    "metric.rain_prob": {"zh_tw": "降雨機率", "en": "Rain Prob."},

    # ── current weather ──
    "current.title": {"zh_tw": "{city} 即時天氣", "en": "{city} Current Weather"},
    "current.no_data": {"zh_tw": "無預報資料", "en": "No forecast data"},

    # ── daily forecast ──
    "daily.title": {"zh_tw": "未來5天天氣預報", "en": "5-Day Weather Forecast"},
    "daily.date_format": {"zh_tw": "{m}月{d}日", "en": "{m}/{d}"},
    "daily.expand_label": {"zh_tw": "{date} ({weekday}) — {tmin}°C ~ {tmax}°C", "en": "{date} ({weekday}) — {tmin}°C ~ {tmax}°C"},

    # ── forecast charts ──
    "forecast.title": {"zh_tw": "天氣預報分析", "en": "Weather Forecast Analysis"},

    # ── chart labels (visualization.py) ──
    "chart.temp_trend": {"zh_tw": "溫度趨勢預報", "en": "Temperature Trend"},
    "chart.actual_temp": {"zh_tw": "實際溫度", "en": "Actual Temp"},
    "chart.feels_like": {"zh_tw": "體感溫度", "en": "Feels Like"},
    "chart.datetime": {"zh_tw": "日期時間", "en": "Date/Time"},
    "chart.temp_unit": {"zh_tw": "溫度 (°C)", "en": "Temperature (°C)"},
    "chart.daily_summary": {"zh_tw": "未來5天溫度預報", "en": "5-Day Temperature Forecast"},
    "chart.date": {"zh_tw": "日期", "en": "Date"},
    "chart.temp_max": {"zh_tw": "最高溫", "en": "High"},
    "chart.temp_avg": {"zh_tw": "平均溫", "en": "Average"},
    "chart.temp_min": {"zh_tw": "最低溫", "en": "Low"},
    "chart.humidity_rain": {"zh_tw": "濕度與降雨機率預報", "en": "Humidity & Rain Probability"},
    "chart.humidity": {"zh_tw": "濕度", "en": "Humidity"},
    "chart.humidity_unit": {"zh_tw": "濕度 (%)", "en": "Humidity (%)"},
    "chart.rain_prob": {"zh_tw": "降雨機率", "en": "Rain Prob."},
    "chart.rain_unit": {"zh_tw": "降雨機率 (%)", "en": "Rain Probability (%)"},
    "chart.daily_pop": {"zh_tw": "未來5天降雨機率", "en": "5-Day Rain Probability"},
    "chart.wind_speed": {"zh_tw": "風速預報", "en": "Wind Speed Forecast"},
    "chart.wind": {"zh_tw": "風速", "en": "Wind Speed"},
    "chart.wind_unit": {"zh_tw": "風速 (m/s)", "en": "Wind Speed (m/s)"},

    # ── api errors (weather_api.py) ──
    "api.error_request": {"zh_tw": "API 請求錯誤: {e}", "en": "API request error: {e}"},
    "api.error_parse": {"zh_tw": "資料解析錯誤: {e}", "en": "Data parsing error: {e}"},
    "api.key_valid": {"zh_tw": "API Key 有效", "en": "API Key is valid"},
    "api.key_invalid": {"zh_tw": "API Key 無效或尚未啟用", "en": "API Key is invalid or not activated"},
    "api.key_fail": {"zh_tw": "驗證失敗 (HTTP {code})", "en": "Verification failed (HTTP {code})"},
    "api.timeout": {"zh_tw": "連線逾時，請稍後再試", "en": "Connection timeout, please try again later"},
    "api.network_error": {"zh_tw": "網路錯誤: {e}", "en": "Network error: {e}"},

    # ── AI analysis (ai_analyzer.py) — GPT prompts ──
    "ai.gpt_system_weather": {
        "zh_tw": "你是一位專業的台灣氣象分析師，擅長解析天氣數據並提供實用建議。",
        "en": "You are a professional weather analyst for Taiwan, skilled at interpreting weather data and providing practical advice.",
    },
    "ai.gpt_prompt_weather": {
        "zh_tw": "你是一位專業的氣象分析師，請根據以下台灣{city}的天氣資料，提供詳細的天氣分析：\n\n{summary}\n\n請提供：\n1. 今日天氣總結（2-3句話）\n2. 未來天氣趨勢分析\n3. 需要特別注意的天氣變化\n\n請用專業但易懂的方式說明，並使用繁體中文。",
        "en": "You are a professional weather analyst. Based on the following weather data for {city}, Taiwan, provide a detailed analysis:\n\n{summary}\n\nPlease provide:\n1. Today's weather summary (2-3 sentences)\n2. Future weather trend analysis\n3. Notable weather changes to watch\n\nUse professional but easy-to-understand language in English.",
    },
    "ai.gpt_system_activities": {
        "zh_tw": "你是一位生活顧問，擅長根據天氣提供實用的活動建議。",
        "en": "You are a lifestyle consultant skilled at providing practical activity suggestions based on weather.",
    },
    "ai.gpt_prompt_activities": {
        "zh_tw": "根據{city}的天氣狀況：\n\n{summary}\n\n請針對今天和未來幾天，推薦5個適合的活動或建議：\n- 戶外活動（如果天氣適合）\n- 室內活動（如果天氣不佳）\n- 運動建議\n- 出遊建議\n- 日常生活建議\n\n每個建議請說明原因，使用繁體中文，以列表方式呈現。",
        "en": "Based on the weather for {city}:\n\n{summary}\n\nRecommend 5 suitable activities for today and the coming days:\n- Outdoor activities (if weather is suitable)\n- Indoor activities (if weather is unfavorable)\n- Exercise suggestions\n- Travel suggestions\n- Daily life tips\n\nExplain the reason for each, in English, as a list.",
    },
    "ai.gpt_system_outfit": {
        "zh_tw": "你是一位時尚顧問，擅長根據天氣提供實用的穿搭建議。",
        "en": "You are a fashion consultant skilled at providing practical outfit suggestions based on weather.",
    },
    "ai.gpt_prompt_outfit": {
        "zh_tw": "根據{city}的天氣：\n\n{summary}\n\n請提供今日和未來幾天的穿搭建議：\n1. 今日穿搭建議（上衣、下著、外套、配件）\n2. 未來3天的穿搭趨勢\n3. 特殊提醒（例如：需要帶傘、防曬等）\n\n請考慮溫度、濕度、降雨機率等因素，使用繁體中文。",
        "en": "Based on the weather for {city}:\n\n{summary}\n\nProvide outfit suggestions for today and the next few days:\n1. Today's outfit (top, bottom, jacket, accessories)\n2. Outfit trends for the next 3 days\n3. Special reminders (e.g. bring umbrella, sunscreen)\n\nConsider temperature, humidity, and rain probability. In English.",
    },
    "ai.gpt_system_health": {
        "zh_tw": "你是一位健康顧問，擅長根據天氣提供健康建議。",
        "en": "You are a health consultant skilled at providing health advice based on weather conditions.",
    },
    "ai.gpt_prompt_health": {
        "zh_tw": "根據{city}的天氣狀況：\n\n{summary}\n\n請提供健康相關建議：\n1. 今日健康注意事項\n2. 運動時間建議\n3. 飲食建議（冷飲/熱飲、補水等）\n4. 特殊族群提醒（老人、小孩、過敏體質）\n5. 未來幾天的健康準備\n\n請用專業但易懂的方式說明，使用繁體中文。",
        "en": "Based on the weather for {city}:\n\n{summary}\n\nProvide health-related advice:\n1. Today's health precautions\n2. Exercise timing suggestions\n3. Diet suggestions (cold/hot drinks, hydration, etc.)\n4. Reminders for vulnerable groups (elderly, children, allergy sufferers)\n5. Health preparations for coming days\n\nUse professional but easy-to-understand language in English.",
    },
    "ai.error": {"zh_tw": "AI分析時發生錯誤: {e}", "en": "AI analysis error: {e}"},
    "ai.gpt_failed_fallback": {
        "zh_tw": "GPT 分析失敗，已切換為基礎規則分析。",
        "en": "GPT analysis failed, switched to rule-based analysis.",
    },
    "ai.subheader_gpt": {"zh_tw": "AI智慧分析（GPT 深度分析）", "en": "AI Analysis (GPT Deep Analysis)"},
    "ai.subheader_rule": {"zh_tw": "AI智慧分析（基礎規則分析）", "en": "AI Analysis (Rule-based)"},
    "ai.upgrade_hint": {
        "zh_tw": "輸入 OpenAI API Key 可升級為 GPT 深度分析模式",
        "en": "Enter OpenAI API Key to upgrade to GPT deep analysis mode",
    },
    "ai.analysis_city": {"zh_tw": "分析城市", "en": "Analysis City"},
    "ai.analysis_time": {"zh_tw": "分析時間", "en": "Analysis Time"},
    "ai.btn_gpt": {"zh_tw": "生成 GPT 深度分析", "en": "Generate GPT Analysis"},
    "ai.btn_rule": {"zh_tw": "生成基礎規則分析", "en": "Generate Rule Analysis"},
    "ai.result_gpt": {"zh_tw": "以下為 GPT 深度分析結果", "en": "GPT deep analysis results below"},
    "ai.result_rule": {
        "zh_tw": "以下為基礎規則分析結果（輸入 OpenAI Key 可升級）",
        "en": "Rule-based analysis results below (enter OpenAI Key to upgrade)",
    },
    "ai.tab_weather": {"zh_tw": "天氣分析", "en": "Weather Analysis"},
    "ai.tab_activities": {"zh_tw": "活動建議", "en": "Activity Tips"},
    "ai.tab_outfit": {"zh_tw": "穿搭建議", "en": "Outfit Tips"},
    "ai.tab_health": {"zh_tw": "健康建議", "en": "Health Tips"},
    "ai.card_weather": {"zh_tw": "專業天氣分析", "en": "Professional Weather Analysis"},
    "ai.card_activities": {"zh_tw": "個人化活動建議", "en": "Personalized Activity Tips"},
    "ai.card_outfit": {"zh_tw": "智慧穿搭建議", "en": "Smart Outfit Tips"},
    "ai.card_health": {"zh_tw": "健康照護建議", "en": "Health Care Tips"},
    "ai.download_btn": {"zh_tw": "下載分析報告", "en": "Download Report"},
    "ai.report_title": {"zh_tw": "智慧天氣分析報告", "en": "Smart Weather Analysis Report"},
    "ai.report_city": {"zh_tw": "城市", "en": "City"},
    "ai.report_time": {"zh_tw": "分析時間", "en": "Analysis Time"},
    "ai.report_mode": {"zh_tw": "分析模式", "en": "Analysis Mode"},
    "ai.report_mode_gpt": {"zh_tw": "GPT 深度分析", "en": "GPT Deep Analysis"},
    "ai.report_mode_rule": {"zh_tw": "基礎規則分析", "en": "Rule-based Analysis"},
    "ai.report_section_weather": {"zh_tw": "天氣分析", "en": "Weather Analysis"},
    "ai.report_section_activities": {"zh_tw": "活動建議", "en": "Activity Tips"},
    "ai.report_section_outfit": {"zh_tw": "穿搭建議", "en": "Outfit Tips"},
    "ai.report_section_health": {"zh_tw": "健康建議", "en": "Health Tips"},

    # ── ai_analyzer.py — GPT summary labels ──
    "ai.summary_current": {"zh_tw": "【即時天氣】", "en": "[Current Weather]"},
    "ai.summary_temp": {"zh_tw": "溫度", "en": "Temperature"},
    "ai.summary_feels": {"zh_tw": "體感", "en": "Feels like"},
    "ai.summary_humidity": {"zh_tw": "濕度", "en": "Humidity"},
    "ai.summary_wind": {"zh_tw": "風速", "en": "Wind speed"},
    "ai.summary_condition": {"zh_tw": "天氣狀況", "en": "Condition"},
    "ai.summary_forecast": {"zh_tw": "【未來5天預報】", "en": "[5-Day Forecast]"},
    "ai.summary_temp_range": {"zh_tw": "溫度", "en": "Temp"},
    "ai.summary_rain": {"zh_tw": "降雨機率", "en": "Rain prob."},

    # ── ai_analyzer.py — Rule engine strings ──
    "rule.today_summary_title": {"zh_tw": "**📋 今日天氣總結**\n", "en": "**📋 Today's Weather Summary**\n"},
    "rule.today_summary": {
        "zh_tw": "目前氣溫 {temp}°C（體感 {feels}°C），{desc}，濕度 {humidity}%，風速 {wind} m/s。\n",
        "en": "Current temperature {temp}°C (feels like {feels}°C), {desc}, humidity {humidity}%, wind {wind} m/s.\n",
    },
    "rule.high_temp_warn": {
        "zh_tw": "- ⚠️ **高溫警告**：氣溫超過 35°C，請避免長時間曝曬，注意防曬補水。\n",
        "en": "- ⚠️ **High Temp Warning**: Over 35°C — avoid prolonged sun exposure, stay hydrated.\n",
    },
    "rule.hot": {"zh_tw": "- 🌡️ 天氣炎熱，建議多補充水分。\n", "en": "- 🌡️ Hot weather — drink plenty of water.\n"},
    "rule.low_temp_warn": {
        "zh_tw": "- ⚠️ **低溫警告**：氣溫低於 10°C，注意保暖，穿著多層衣物。\n",
        "en": "- ⚠️ **Low Temp Warning**: Below 10°C — stay warm, wear layers.\n",
    },
    "rule.cool": {"zh_tw": "- 🧣 天氣偏涼，建議攜帶外套。\n", "en": "- 🧣 Cool weather — bring a jacket.\n"},
    "rule.comfortable": {"zh_tw": "- ✅ 氣溫舒適宜人。\n", "en": "- ✅ Comfortable temperature.\n"},
    "rule.high_humidity": {
        "zh_tw": "- 💧 濕度偏高（>80%），體感悶熱，建議待在通風處。\n",
        "en": "- 💧 High humidity (>80%) — feels muggy, stay in ventilated areas.\n",
    },
    "rule.low_humidity": {
        "zh_tw": "- 🏜️ 濕度偏低，注意皮膚保濕。\n",
        "en": "- 🏜️ Low humidity — moisturize your skin.\n",
    },
    "rule.strong_wind": {
        "zh_tw": "- 💨 風速較大（>10 m/s），外出注意安全，避免山區活動。\n",
        "en": "- 💨 Strong wind (>10 m/s) — be careful outdoors, avoid mountain areas.\n",
    },
    "rule.breeze": {"zh_tw": "- 🍃 微風吹拂，體感較涼爽。\n", "en": "- 🍃 Gentle breeze — feels refreshing.\n"},
    "rule.trend_title": {"zh_tw": "\n**📈 未來天氣趨勢**\n", "en": "\n**📈 Future Weather Trend**\n"},
    "rule.trend_warming": {
        "zh_tw": "- 未來幾天氣溫**逐漸升高**，請注意防暑。\n",
        "en": "- Temperatures will **rise gradually** — watch for heat.\n",
    },
    "rule.trend_cooling": {
        "zh_tw": "- 未來幾天氣溫**逐漸下降**，請注意保暖。\n",
        "en": "- Temperatures will **drop gradually** — stay warm.\n",
    },
    "rule.trend_stable": {
        "zh_tw": "- 未來幾天氣溫**相對穩定**。\n",
        "en": "- Temperatures will remain **relatively stable**.\n",
    },
    "rule.rain_many": {
        "zh_tw": "- 🌧️ 未來 5 天中有 {n} 天降雨機率偏高，建議備好雨具。\n",
        "en": "- 🌧️ {n} of the next 5 days have high rain probability — bring rain gear.\n",
    },
    "rule.rain_some": {
        "zh_tw": "- 🌂 部分天數有降雨可能（{n} 天），出門可攜帶雨傘。\n",
        "en": "- 🌂 Some days may have rain ({n} days) — consider carrying an umbrella.\n",
    },
    "rule.rain_none": {
        "zh_tw": "- ☀️ 未來幾天降雨機率不高，天氣大致晴朗。\n",
        "en": "- ☀️ Low rain probability — mostly sunny ahead.\n",
    },
    "rule.daily_overview_title": {"zh_tw": "\n**📅 每日概覽**\n", "en": "\n**📅 Daily Overview**\n"},
    "rule.daily_overview_row": {
        "zh_tw": "- {date}（{weekday}）：{tmin}°C ~ {tmax}°C，降雨 {pop}% {icon}，{weather}\n",
        "en": "- {date} ({weekday}): {tmin}°C ~ {tmax}°C, rain {pop}% {icon}, {weather}\n",
    },

    # rule — activities
    "rule.act_title": {"zh_tw": "**🎯 今日活動建議**\n\n", "en": "**🎯 Today's Activity Tips**\n\n"},
    "rule.act_outdoor_ok": {"zh_tw": "✅ 今天天氣適合戶外活動！\n\n", "en": "✅ Great weather for outdoor activities!\n\n"},
    "rule.act_swim": {
        "zh_tw": "- 🏊 **水上活動**：天氣炎熱，適合游泳、玩水消暑。\n",
        "en": "- 🏊 **Water sports**: Hot weather — great for swimming and water fun.\n",
    },
    "rule.act_evening_walk": {
        "zh_tw": "- 🌅 **傍晚散步**：避開正午高溫，建議傍晚時分到公園散步。\n",
        "en": "- 🌅 **Evening walk**: Avoid midday heat — take a park stroll in the evening.\n",
    },
    "rule.act_cycling": {
        "zh_tw": "- 🚴 **自行車騎行**：氣溫舒適，適合戶外騎行運動。\n",
        "en": "- 🚴 **Cycling**: Comfortable temps — perfect for an outdoor ride.\n",
    },
    "rule.act_hiking": {
        "zh_tw": "- 🥾 **健行登山**：天氣涼爽，適合步道健行。\n",
        "en": "- 🥾 **Hiking**: Cool weather — great for trail hiking.\n",
    },
    "rule.act_photo": {
        "zh_tw": "- 📸 **戶外攝影**：濕度適中，適合外出拍照。\n",
        "en": "- 📸 **Photography**: Moderate humidity — ideal for outdoor shots.\n",
    },
    "rule.act_outdoor_no": {
        "zh_tw": "⚠️ 今天較不適合長時間戶外活動。\n\n",
        "en": "⚠️ Not ideal for prolonged outdoor activities today.\n\n",
    },
    "rule.act_reason_hot": {"zh_tw": "氣溫過高", "en": "Temperature too high"},
    "rule.act_reason_cold": {"zh_tw": "氣溫偏低", "en": "Temperature too low"},
    "rule.act_reason_rain": {"zh_tw": "降雨機率高", "en": "High rain probability"},
    "rule.act_reason_wind": {"zh_tw": "風速過大", "en": "Too windy"},
    "rule.act_reason_prefix": {"zh_tw": "- 原因：{reasons}\n", "en": "- Reason: {reasons}\n"},
    "rule.act_indoor_movie": {
        "zh_tw": "- 🎬 **室內活動**：建議看電影、逛書店、參觀展覽。\n",
        "en": "- 🎬 **Indoor**: Movies, bookstores, or exhibitions.\n",
    },
    "rule.act_indoor_gym": {
        "zh_tw": "- 🏋️ **室內運動**：可到健身房、室內游泳池運動。\n",
        "en": "- 🏋️ **Indoor exercise**: Gym or indoor swimming pool.\n",
    },
    "rule.act_indoor_cafe": {
        "zh_tw": "- ☕ **咖啡廳休閒**：找間舒適的咖啡廳，享受悠閒時光。\n",
        "en": "- ☕ **Cafe time**: Relax at a cozy cafe.\n",
    },
    "rule.act_exercise_title": {
        "zh_tw": "\n**🏃 運動建議**\n\n",
        "en": "\n**🏃 Exercise Tips**\n\n",
    },
    "rule.act_exercise_hot": {
        "zh_tw": "- 建議在清晨（6-8時）或傍晚（17-19時）運動，避開高溫時段。\n",
        "en": "- Exercise in early morning (6-8am) or evening (5-7pm) to avoid peak heat.\n",
    },
    "rule.act_exercise_cold": {
        "zh_tw": "- 運動前務必做好暖身，避免肌肉拉傷。\n",
        "en": "- Warm up thoroughly before exercising to avoid injury.\n",
    },
    "rule.act_exercise_normal": {
        "zh_tw": "- 氣溫適中，適合全天運動，記得補充水分。\n",
        "en": "- Comfortable temps — exercise anytime, stay hydrated.\n",
    },

    # rule — outfit
    "rule.outfit_title": {"zh_tw": "**👔 今日穿搭建議**\n\n", "en": "**👔 Today's Outfit Tips**\n\n"},
    "rule.outfit_hot_top": {
        "zh_tw": "- 👕 **上衣**：短袖、透氣材質（棉、麻），淺色系較佳。\n",
        "en": "- 👕 **Top**: Short sleeves, breathable fabrics (cotton, linen), light colors.\n",
    },
    "rule.outfit_hot_bottom": {
        "zh_tw": "- 👖 **下著**：短褲、薄長褲或裙裝。\n",
        "en": "- 👖 **Bottom**: Shorts, light pants, or skirts.\n",
    },
    "rule.outfit_hot_acc": {
        "zh_tw": "- 🧢 **配件**：太陽眼鏡、遮陽帽、防曬乳。\n",
        "en": "- 🧢 **Accessories**: Sunglasses, sun hat, sunscreen.\n",
    },
    "rule.outfit_warm_top": {
        "zh_tw": "- 👕 **上衣**：短袖或薄長袖 T-shirt。\n",
        "en": "- 👕 **Top**: Short sleeves or light long-sleeve T-shirt.\n",
    },
    "rule.outfit_warm_bottom": {
        "zh_tw": "- 👖 **下著**：長褲或短褲皆可。\n",
        "en": "- 👖 **Bottom**: Pants or shorts.\n",
    },
    "rule.outfit_warm_jacket": {
        "zh_tw": "- 🧥 **外套**：室內冷氣房可備薄外套。\n",
        "en": "- 🧥 **Jacket**: Light jacket for air-conditioned rooms.\n",
    },
    "rule.outfit_mild_top": {
        "zh_tw": "- 👕 **上衣**：長袖上衣、薄毛衣。\n",
        "en": "- 👕 **Top**: Long-sleeve shirt, light sweater.\n",
    },
    "rule.outfit_mild_bottom": {
        "zh_tw": "- 👖 **下著**：長褲為主。\n",
        "en": "- 👖 **Bottom**: Long pants.\n",
    },
    "rule.outfit_mild_jacket": {
        "zh_tw": "- 🧥 **外套**：薄外套或針織衫。\n",
        "en": "- 🧥 **Jacket**: Light jacket or cardigan.\n",
    },
    "rule.outfit_cool_top": {
        "zh_tw": "- 👕 **上衣**：長袖上衣 + 毛衣。\n",
        "en": "- 👕 **Top**: Long-sleeve shirt + sweater.\n",
    },
    "rule.outfit_cool_bottom": {
        "zh_tw": "- 👖 **下著**：長褲、牛仔褲。\n",
        "en": "- 👖 **Bottom**: Long pants, jeans.\n",
    },
    "rule.outfit_cool_jacket": {
        "zh_tw": "- 🧥 **外套**：風衣、夾克或厚外套。\n",
        "en": "- 🧥 **Jacket**: Trench coat, jacket, or heavy coat.\n",
    },
    "rule.outfit_cool_acc": {
        "zh_tw": "- 🧣 **配件**：圍巾備用。\n",
        "en": "- 🧣 **Accessories**: Scarf as backup.\n",
    },
    "rule.outfit_cold_top": {
        "zh_tw": "- 👕 **上衣**：多層穿搭 — 內搭 + 毛衣 + 外套。\n",
        "en": "- 👕 **Top**: Layer up — base + sweater + jacket.\n",
    },
    "rule.outfit_cold_bottom": {
        "zh_tw": "- 👖 **下著**：厚長褲，可考慮內搭褲。\n",
        "en": "- 👖 **Bottom**: Thick pants, consider thermal leggings.\n",
    },
    "rule.outfit_cold_jacket": {
        "zh_tw": "- 🧥 **外套**：厚外套、羽絨衣。\n",
        "en": "- 🧥 **Jacket**: Heavy coat, down jacket.\n",
    },
    "rule.outfit_cold_acc": {
        "zh_tw": "- 🧣 **配件**：圍巾、手套、毛帽。\n",
        "en": "- 🧣 **Accessories**: Scarf, gloves, beanie.\n",
    },
    "rule.outfit_rain_must": {
        "zh_tw": "\n- 🌂 **必備雨具**：降雨機率高，請攜帶雨傘或穿防水外套。\n",
        "en": "\n- 🌂 **Rain gear required**: High rain probability — bring umbrella or waterproof jacket.\n",
    },
    "rule.outfit_rain_maybe": {
        "zh_tw": "\n- 🌂 **建議帶傘**：有降雨可能，建議備用雨傘。\n",
        "en": "\n- 🌂 **Bring umbrella**: Possible rain — have an umbrella handy.\n",
    },
    "rule.outfit_humid": {
        "zh_tw": "- 💧 濕度高，衣物建議選擇吸濕排汗材質。\n",
        "en": "- 💧 High humidity — choose moisture-wicking fabrics.\n",
    },
    "rule.outfit_future_title": {
        "zh_tw": "\n**📅 未來穿搭趨勢**\n\n",
        "en": "\n**📅 Outfit Trend Ahead**\n\n",
    },
    "rule.outfit_future_colder": {
        "zh_tw": "- 未來幾天氣溫將明顯下降，請準備較厚的衣物。\n",
        "en": "- Temperatures will drop significantly — prepare warmer clothes.\n",
    },
    "rule.outfit_future_warmer": {
        "zh_tw": "- 未來幾天氣溫將上升，可準備較輕便的穿著。\n",
        "en": "- Temperatures will rise — lighter clothing ahead.\n",
    },
    "rule.outfit_future_stable": {
        "zh_tw": "- 未來幾天氣溫變化不大，穿搭可維持今日風格。\n",
        "en": "- Temperatures will stay similar — stick with today's style.\n",
    },
    "rule.outfit_future_rain": {
        "zh_tw": "- 未來幾天有降雨可能，建議隨身攜帶雨具。\n",
        "en": "- Rain possible in coming days — keep rain gear handy.\n",
    },

    # rule — health
    "rule.health_title": {"zh_tw": "**💪 今日健康注意事項**\n\n", "en": "**💪 Today's Health Notes**\n\n"},
    "rule.health_heatstroke": {
        "zh_tw": "- ⚠️ **中暑風險**：高溫環境下請注意以下事項：\n  - 每小時至少補充 250ml 水分\n  - 避免 10:00-15:00 曝曬\n  - 出現頭暈、噁心請立即至陰涼處休息\n",
        "en": "- ⚠️ **Heatstroke risk**: In high temps:\n  - Drink at least 250ml water per hour\n  - Avoid sun exposure 10am-3pm\n  - If dizzy or nauseous, rest in shade immediately\n",
    },
    "rule.health_warm": {
        "zh_tw": "- 🌡️ 天氣偏熱，注意補充水分，建議每日飲水 2000ml 以上。\n",
        "en": "- 🌡️ Warm weather — stay hydrated, drink 2000ml+ daily.\n",
    },
    "rule.health_cold_warn": {
        "zh_tw": "- ⚠️ **低溫注意**：\n  - 心血管疾病患者注意保暖\n  - 避免突然激烈運動\n  - 起床時先在被窩暖身再起身\n",
        "en": "- ⚠️ **Cold weather warning**:\n  - Cardiovascular patients: stay warm\n  - Avoid sudden intense exercise\n  - Warm up in bed before getting up\n",
    },
    "rule.health_cool": {
        "zh_tw": "- 🧣 天氣偏涼，出門注意保暖，預防感冒。\n",
        "en": "- 🧣 Cool weather — stay warm to prevent colds.\n",
    },
    "rule.health_humid": {
        "zh_tw": "- 💧 **高濕警示**：濕度偏高可能加重過敏症狀。\n  - 過敏體質者建議使用除濕機\n  - 注意食物保鮮，避免細菌滋生\n",
        "en": "- 💧 **High humidity alert**: May worsen allergies.\n  - Allergy sufferers: use a dehumidifier\n  - Keep food fresh to prevent bacterial growth\n",
    },
    "rule.health_dry": {
        "zh_tw": "- 🏜️ 空氣乾燥，注意皮膚保濕、多喝水，可使用加濕器。\n",
        "en": "- 🏜️ Dry air — moisturize skin, drink more water, use a humidifier.\n",
    },
    "rule.health_wind": {
        "zh_tw": "- 💨 風大注意：外出時注意眼睛防護，配戴口罩防風沙。\n",
        "en": "- 💨 Windy — protect eyes outdoors, wear a mask against dust.\n",
    },
    "rule.health_exercise_title": {
        "zh_tw": "\n**🏃 運動時間建議**\n\n",
        "en": "\n**🏃 Exercise Timing Tips**\n\n",
    },
    "rule.health_exercise_hot": {
        "zh_tw": "- ⏰ 最佳運動時段：清晨 06:00-08:00 或傍晚 17:00-19:00\n- 避免正午時段戶外運動\n",
        "en": "- ⏰ Best time: 6-8am or 5-7pm\n- Avoid outdoor exercise at midday\n",
    },
    "rule.health_exercise_cold": {
        "zh_tw": "- ⏰ 最佳運動時段：上午 10:00-12:00（氣溫回升後）\n- 運動前充分暖身 10-15 分鐘\n",
        "en": "- ⏰ Best time: 10am-12pm (after warming up)\n- Warm up 10-15 min before exercising\n",
    },
    "rule.health_exercise_normal": {
        "zh_tw": "- ⏰ 全天皆適合運動，記得做好暖身與收操。\n",
        "en": "- ⏰ Exercise anytime — warm up and cool down properly.\n",
    },
    "rule.health_diet_title": {"zh_tw": "\n**🍽️ 飲食建議**\n\n", "en": "\n**🍽️ Diet Tips**\n\n"},
    "rule.health_diet_hot": {
        "zh_tw": "- 多喝水、少量多次補充電解質\n- 可飲用綠豆湯、仙草等消暑飲品\n- 避免過多冰品，以免腸胃不適\n",
        "en": "- Drink water frequently, replenish electrolytes\n- Try cooling drinks like mung bean soup\n- Avoid excessive icy drinks to prevent stomach issues\n",
    },
    "rule.health_diet_cold": {
        "zh_tw": "- 適合喝熱湯、薑茶等暖身飲品\n- 多攝取富含維生素C的食物增強免疫力\n",
        "en": "- Enjoy hot soup and ginger tea\n- Eat vitamin C-rich foods to boost immunity\n",
    },
    "rule.health_diet_normal": {
        "zh_tw": "- 氣溫適中，均衡飲食即可，每日建議飲水 1500-2000ml。\n",
        "en": "- Comfortable temps — balanced diet, drink 1500-2000ml daily.\n",
    },
    "rule.health_special_title": {
        "zh_tw": "\n**👴👶 特殊族群提醒**\n\n",
        "en": "\n**👴👶 Special Groups Reminder**\n\n",
    },
    "rule.health_elderly": {
        "zh_tw": "- **長者**：注意室內外溫差，進出冷氣房時緩步適應。\n",
        "en": "- **Elderly**: Watch indoor/outdoor temp differences, adjust gradually.\n",
    },
    "rule.health_children": {
        "zh_tw": "- **幼童**：注意體溫調節，適時增減衣物。\n",
        "en": "- **Children**: Monitor body temperature, adjust clothing as needed.\n",
    },
    "rule.health_allergy": {
        "zh_tw": "- **過敏體質**：高濕環境容易誘發過敏，建議保持居家乾燥通風。\n",
        "en": "- **Allergy sufferers**: High humidity triggers allergies — keep home dry and ventilated.\n",
    },
    "rule.health_asthma": {
        "zh_tw": "- **氣喘患者**：降雨前後氣壓變化大，注意攜帶藥物。\n",
        "en": "- **Asthma patients**: Pressure changes around rain — carry medication.\n",
    },

    # ── alerts (alerts.py) ──
    "alert.section_title": {"zh_tw": "天氣警報", "en": "Weather Alerts"},
    "alert.extreme_heat_title": {"zh_tw": "極端高溫警報", "en": "Extreme Heat Alert"},
    "alert.extreme_heat_msg": {
        "zh_tw": "氣溫達 {v}°C（超過 {t}°C），有嚴重中暑風險，請儘量待在室內。",
        "en": "Temperature at {v}°C (over {t}°C) — serious heatstroke risk, stay indoors.",
    },
    "alert.high_temp_title": {"zh_tw": "高溫注意", "en": "High Temperature Caution"},
    "alert.high_temp_msg": {
        "zh_tw": "氣溫達 {v}°C（超過 {t}°C），請注意防曬補水。",
        "en": "Temperature at {v}°C (over {t}°C) — apply sunscreen, stay hydrated.",
    },
    "alert.extreme_cold_title": {"zh_tw": "極端低溫警報", "en": "Extreme Cold Alert"},
    "alert.extreme_cold_msg": {
        "zh_tw": "氣溫僅 {v}°C（低於 {t}°C），心血管疾病患者請特別注意保暖。",
        "en": "Temperature at {v}°C (below {t}°C) — cardiovascular patients, stay warm.",
    },
    "alert.low_temp_title": {"zh_tw": "低溫注意", "en": "Low Temperature Caution"},
    "alert.low_temp_msg": {
        "zh_tw": "氣溫僅 {v}°C（低於 {t}°C），請注意保暖。",
        "en": "Temperature at {v}°C (below {t}°C) — stay warm.",
    },
    "alert.strong_wind_title": {"zh_tw": "強風警報", "en": "Strong Wind Alert"},
    "alert.strong_wind_msg": {
        "zh_tw": "風速達 {v} m/s（超過 {t} m/s），外出請注意安全。",
        "en": "Wind speed {v} m/s (over {t} m/s) — be careful outdoors.",
    },
    "alert.high_wind_title": {"zh_tw": "大風注意", "en": "High Wind Caution"},
    "alert.high_wind_msg": {
        "zh_tw": "風速達 {v} m/s（超過 {t} m/s），避免山區活動。",
        "en": "Wind speed {v} m/s (over {t} m/s) — avoid mountain activities.",
    },
    "alert.high_humidity_title": {"zh_tw": "高濕注意", "en": "High Humidity Caution"},
    "alert.high_humidity_msg": {
        "zh_tw": "濕度達 {v}%（超過 {t}%），體感悶熱，過敏體質請留意。",
        "en": "Humidity at {v}% (over {t}%) — muggy, allergy sufferers beware.",
    },
    "alert.heavy_rain_title": {"zh_tw": "暴雨警報", "en": "Heavy Rain Alert"},
    "alert.heavy_rain_msg": {
        "zh_tw": "降雨機率達 {v}%（超過 {t}%），外出請備好雨具。",
        "en": "Rain probability {v}% (over {t}%) — bring rain gear.",
    },
    "alert.rain_title": {"zh_tw": "降雨注意", "en": "Rain Caution"},
    "alert.rain_msg": {
        "zh_tw": "降雨機率達 {v}%（超過 {t}%），建議攜帶雨傘。",
        "en": "Rain probability {v}% (over {t}%) — bring an umbrella.",
    },
    "alert.temp_swing_title": {"zh_tw": "日溫差大", "en": "Large Temperature Swing"},
    "alert.temp_swing_msg": {
        "zh_tw": "日溫差達 {v}°C（超過 {t}°C），請注意適時增減衣物。",
        "en": "Daily temp swing {v}°C (over {t}°C) — adjust clothing accordingly.",
    },
    "alert.official_title": {"zh_tw": "官方天氣警報", "en": "Official Weather Alert"},

    # ── weekday names ──
    "weekday.0": {"zh_tw": "一", "en": "Mon"},
    "weekday.1": {"zh_tw": "二", "en": "Tue"},
    "weekday.2": {"zh_tw": "三", "en": "Wed"},
    "weekday.3": {"zh_tw": "四", "en": "Thu"},
    "weekday.4": {"zh_tw": "五", "en": "Fri"},
    "weekday.5": {"zh_tw": "六", "en": "Sat"},
    "weekday.6": {"zh_tw": "日", "en": "Sun"},
}


def get_lang() -> str:
    """取得當前語言設定（從 session_state）"""
    try:
        return st.session_state.get("ui_lang", "zh_tw")
    except Exception:
        return "zh_tw"


def t(key: str, **kwargs) -> str:
    """
    翻譯函式

    Args:
        key: 翻譯鍵值（如 "sidebar.title"）
        **kwargs: format 參數

    Returns:
        翻譯後的字串，找不到時回傳 key 本身
    """
    lang = get_lang()
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(lang, entry.get("zh_tw", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def weekday_name(idx: int) -> str:
    """
    星期名稱 (0=Mon, 1=Tue, ... 6=Sun)
    """
    return t(f"weekday.{idx}")
