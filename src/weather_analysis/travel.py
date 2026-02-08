"""
旅遊最佳日推薦模組 - 根據天氣評分推薦最佳出遊日
"""


def score_day(day_summary: dict) -> dict:
    """
    為每日天氣打分（0-100），回傳分數與各維度細項。

    評分維度：
    - 溫度舒適度 (40 分)：18-26°C 滿分，偏離每度扣 3 分
    - 降雨機率 (25 分)：pop 每 10% 扣 2.5 分
    - 風速 (15 分)：<=5 滿分，>5 後每 1 m/s 扣 3 分
    - 濕度 (20 分)：40-70% 滿分，偏離每 5% 扣 2 分
    """
    temp = day_summary.get("temp_avg", 22)
    pop = day_summary.get("pop_max", 0)
    wind = day_summary.get("wind_speed_avg", 0)
    humidity = day_summary.get("humidity_avg", 60)

    # 溫度 (40 分)
    if 18 <= temp <= 26:
        temp_score = 40
    else:
        diff = min(abs(temp - 18), abs(temp - 26))
        if temp < 18:
            diff = 18 - temp
        else:
            diff = temp - 26
        temp_score = max(0, 40 - diff * 3)

    # 降雨 (25 分)
    rain_score = max(0, 25 - pop / 10 * 2.5)

    # 風速 (15 分)
    if wind <= 5:
        wind_score = 15
    else:
        wind_score = max(0, 15 - (wind - 5) * 3)

    # 濕度 (20 分)
    if 40 <= humidity <= 70:
        humidity_score = 20
    else:
        if humidity < 40:
            diff = 40 - humidity
        else:
            diff = humidity - 70
        humidity_score = max(0, 20 - diff / 5 * 2)

    total = round(temp_score + rain_score + wind_score + humidity_score, 1)

    return {
        "total": total,
        "temp_score": round(temp_score, 1),
        "rain_score": round(rain_score, 1),
        "wind_score": round(wind_score, 1),
        "humidity_score": round(humidity_score, 1),
    }


def _build_reasons(day_summary: dict, scores: dict) -> list[str]:
    """根據各維度分數產生推薦/警告原因的 i18n key 列表"""
    reasons = []
    temp = day_summary.get("temp_avg", 22)
    pop = day_summary.get("pop_max", 0)
    wind = day_summary.get("wind_speed_avg", 0)

    # 正面原因
    if scores["temp_score"] >= 34:
        reasons.append("travel.reason_temp_good")
    elif temp > 30:
        reasons.append("travel.reason_temp_hot")
    elif temp < 15:
        reasons.append("travel.reason_temp_cold")

    if scores["rain_score"] >= 20:
        reasons.append("travel.reason_rain_low")
    elif pop >= 60:
        reasons.append("travel.reason_rain_high")

    if scores["wind_score"] >= 12:
        reasons.append("travel.reason_wind_calm")
    elif wind > 8:
        reasons.append("travel.reason_wind_strong")

    if scores["humidity_score"] >= 16:
        reasons.append("travel.reason_humidity_good")

    return reasons


def recommend_best_days(daily_summary: list[dict]) -> list[dict]:
    """
    回傳排序後的推薦列表。

    Returns:
        list[dict]: 每項包含 date, score, scores, reasons, recommended, ...原始天氣資料
    """
    if not daily_summary:
        return []

    results = []
    for day in daily_summary:
        scores = score_day(day)
        reasons = _build_reasons(day, scores)
        results.append({
            "date": day["date"],
            "score": scores["total"],
            "scores": scores,
            "reasons": reasons,
            "temp_avg": day.get("temp_avg", 0),
            "pop_max": day.get("pop_max", 0),
            "wind_speed_avg": day.get("wind_speed_avg", 0),
            "humidity_avg": day.get("humidity_avg", 0),
            "weather": day.get("weather", ""),
            "icon": day.get("icon", "01d"),
            "recommended": False,
        })

    # 按分數排序（高到低）
    results.sort(key=lambda x: x["score"], reverse=True)

    # 標記前 2 名為推薦
    for i in range(min(2, len(results))):
        results[i]["recommended"] = True

    # 回復為日期排序以便顯示
    results.sort(key=lambda x: x["date"])

    return results
