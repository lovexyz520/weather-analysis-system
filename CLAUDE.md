# 智慧天氣分析系統 — 系統規格書

## 專案概述

- **名稱**: weather-analysis-system（智慧天氣分析系統）
- **版本**: 1.2.0
- **語言**: Python 3.10+
- **框架**: Streamlit
- **用途**: 台灣 12 城市即時天氣查詢 + AI 智慧分析（GPT / 規則引擎）+ 旅遊推薦 + 城市比較 + AQI + 天氣地圖

## 啟動方式

```bash
uv sync                                              # 安裝依賴
uv run streamlit run src/weather_analysis/app.py     # 啟動應用
```

## 專案結構

```
weather-analysis-system/
├── pyproject.toml              # 專案設定（uv + hatchling build backend）
├── requirements.txt            # Streamlit Cloud 部署用依賴清單
├── .env.example                # 環境變數範例
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example    # Streamlit Cloud secrets 範例
├── CLAUDE.md                   # 本規格書
├── README.md
└── src/
    └── weather_analysis/       # 主套件
        ├── __init__.py         # 版本號 __version__
        ├── app.py              # Streamlit 主程式（UI + 路由，8 個 tab）
        ├── config.py           # 設定檔（API Key 載入 + 常數）
        ├── weather_api.py      # OpenWeatherMap API 整合
        ├── visualization.py    # Plotly 圖表生成（全部 @staticmethod）
        ├── ai_analyzer.py      # AI 分析（GPT + 規則引擎 fallback）
        ├── i18n.py             # 多語言支援（繁中 / English）
        ├── alerts.py           # 天氣警報（規則 + One Call 3.0 官方）
        ├── travel.py           # 旅遊最佳日推薦（評分系統）
        └── aqi_api.py          # 空氣品質 AQI（環境部開放資料）
└── tests/                      # 單元測試（99 tests）
    ├── __init__.py
    ├── test_travel.py          # 旅遊評分邏輯
    ├── test_aqi.py             # AQI 分級 / 城市查詢
    ├── test_alerts.py          # 天氣警報觸發
    └── test_uv.py              # UV 指數分級
```

## 模組職責

### config.py
- `get_env_api_key(key_name, placeholder)` — 統一 API Key 載入邏輯
  - 優先順序：`.env` 環境變數 → `st.secrets`（Streamlit Cloud）
  - 回傳空字串代表未設定
- `OPENAI_MODEL` = `gpt-4o-mini`
- `AQI_API_KEY` — 環境部 AQI API 金鑰（可選）
- `ONECALL_API_KEY` / `ONECALL_BASE_URL` — One Call API 3.0（可選，付費）
- `TAIWAN_CITIES` — 台灣 12 城市中英對照 dict
- `TAIWAN_CITIES_I18N` — 雙語城市名稱對照（供 i18n 使用）
- `TAIWAN_CITIES_COORDS` — 12 城市經緯度（供 One Call API / 地圖使用）
- 常數：`DEFAULT_CITY`, `FORECAST_DAYS`, `UNITS`, `LANG`, `AI_MAX_TOKENS`, `CACHE_EXPIRE_MINUTES`

### i18n.py
- `SUPPORTED_LANGS` = `{"zh_tw": "繁體中文", "en": "English"}`
- `TRANSLATIONS` — 所有翻譯 key/value 集中管理（~320 key）
- `t(key, **kwargs)` — 翻譯函式，支援 format 參數
- `get_lang()` — 從 `st.session_state.ui_lang` 取得當前語言
- `weekday_name(idx)` — 星期名稱（0=Mon ... 6=Sun）

### app.py
- **`_get_active_api_key(session_key, env_default)`** — 取得生效的 API Key
  - 優先順序：sidebar 使用者輸入（`st.session_state`）> `.env` / `st.secrets`
- **`_inject_theme_css()`** — CSS 注入（深色模式 + RWD + 骨架屏動畫）
- **`display_sidebar()`** — 側邊欄結構：
  - 語言選擇器（最頂部）
  - 🔑 API Key 設定（4 個 password input：OWM / OpenAI / One Call / AQI）
  - 偵測到 .env 時只顯示「✅ 已從環境變數載入」文字，不洩漏 Key 值
  - 城市選擇 → 更新按鈕 → 系統資訊
- **`fetch_weather_data(city)`** — 每次呼叫都用最新的 active key 建立 `WeatherAPI` 實例
- **`display_weather_alerts()`** — 天氣警報顯示（在 tabs 上方）
- **`display_current_weather()`** — 即時天氣 tab（含 UV 指數卡片、分享功能）
- **`display_forecast_charts()`** — 預報圖表 tab（含溫度/降雨熱力圖）
- **`display_daily_forecast_table()`** — 每日預報 tab（含 RWD 桌面/手機版）
- **`display_ai_analysis()`** — AI 分析 tab（GPT / 規則引擎）
- **`display_travel_recommendation()`** — 旅遊推薦 tab（v1.2 新增）
- **`display_city_comparison()`** — 多城市比較 tab（v1.2 新增，使用 `@st.fragment` 防止 tab 跳轉）
- **`display_aqi()`** — 空氣品質 tab（v1.2 新增）
- **`display_weather_map()`** — 天氣地圖 tab（v1.2 新增）
- CSS 樣式：`[data-testid="stMetric"]` 使用漸層紫色背景 + 白字

### weather_api.py
- `WeatherAPI` 類別：封裝 OpenWeatherMap API 呼叫
- `get_current_weather(city)` — 即時天氣（回傳 dict 或 None）
- `get_forecast(city)` — 5 天 / 每 3 小時預報（回傳 list 或 None）
- `get_daily_forecast_summary(city)` — 整理為每日摘要
- `get_weather_icon_url(icon_code)` — **@staticmethod**，app.py 以 `WeatherAPI.get_weather_icon_url()` 呼叫
- `get_city_display_name(city_en)` — **@staticmethod**，依當前語言回傳城市顯示名稱
- `validate_key(api_key)` — **@staticmethod**，輕量驗證 OWM API Key
- `_cached_onecall_uvi(api_key, lat, lon)` — 模組層級，One Call API 取得 UV 指數（`@st.cache_data`）
- `get_uv_level(uvi)` — 模組層級，UV 指數 5 級分類，回傳 (i18n key, 顏色 hex)

### visualization.py
- `WeatherCharts` 類別：全部為 **@staticmethod**
- `create_temperature_chart(forecast_data)` — 溫度趨勢折線圖
- `create_daily_summary_chart(daily_summary)` — 每日高低溫柱狀圖
- `create_humidity_rain_chart(forecast_data)` — 雙 Y 軸（濕度 + 降雨機率）
- `create_daily_pop_chart(daily_summary)` — 每日降雨機率（含背景色區域）
- `create_wind_speed_chart(forecast_data)` — 風速面積圖
- `create_comparison_temp_chart(city_data_list)` — 多城市溫度比較折線圖（v1.2 新增）
- `create_comparison_rain_chart(city_data_list)` — 多城市降雨機率比較柱狀圖（v1.2 新增）
- `create_travel_radar_chart(scores)` — 旅遊評分雷達圖（v1.2 新增）
- `create_temp_heatmap(forecast_data)` — 溫度熱力圖：X=時段, Y=日期, Z=溫度（v1.2 新增）
- `create_rain_heatmap(forecast_data)` — 降雨機率熱力圖：X=時段, Y=日期, Z=降雨%（v1.2 新增）
- `_get_plotly_template()` — 模組層級，根據 Streamlit 主題返回 Plotly 模板

### ai_analyzer.py
- `WeatherAIAnalyzer` 類別

**GPT 分析（有 OpenAI Key 時）：**
- `analyze_weather()` — 天氣趨勢分析
- `suggest_activities()` — 活動建議
- `suggest_outfit()` — 穿搭建議
- `health_advice()` — 健康建議
- `_call_openai(system_msg, user_msg, temperature)` — 統一 API 呼叫封裝

**規則引擎 Fallback（無 Key 或 GPT 失敗時）：**
- `get_fallback_analysis(current_weather, daily_summary)` — 入口，回傳 dict
- `_rule_weather_analysis()` — 基於溫度/濕度/風速/降雨閾值的天氣分析
- `_rule_activities()` — 戶外/室內活動判斷邏輯
- `_rule_outfit()` — 依溫度區間（>30, >25, >20, >15, <=15）的穿搭規則
- `_rule_health()` — 健康建議（含運動時間、飲食、特殊族群）

**綜合分析入口：**
- `comprehensive_analysis(current_weather, daily_summary)` → dict
  - 有 Key → GPT 分析，若 4 個項目全部失敗 → 自動 fallback
  - 無 Key → 直接使用規則引擎
  - 回傳 dict 包含 `mode` 欄位：`"gpt"` 或 `"fallback"`

### alerts.py
- `evaluate_alerts(current_weather, daily_summary)` — 規則式天氣警報
- `evaluate_onecall_alerts(api_key, lat, lon)` — One Call 3.0 官方警報
- `AlertSeverity` — 警報嚴重等級（WARNING / DANGER）

### travel.py（v1.2 新增）
- `score_day(day_summary)` — 為每日天氣打分（0-100），回傳各維度分數
  - 溫度舒適度 (40 分)：18-26°C 滿分，偏離每度扣 3 分
  - 降雨機率 (25 分)：pop 每 10% 扣 2.5 分
  - 風速 (15 分)：≤5 滿分，>5 後每 1 m/s 扣 3 分
  - 濕度 (20 分)：40-70% 滿分，偏離每 5% 扣 2 分
- `recommend_best_days(daily_summary)` — 回傳排序後的推薦列表，標記 top 2 為推薦

### aqi_api.py（v1.2 新增）
- `AQI_API_URL` = `https://data.moenv.gov.tw/api/v2/aqx_p_432`
- `CITY_COUNTY_MAP` — 英文城市名 → 環境部 County 欄位值
- `fetch_aqi_data(api_key)` — 取得全台 AQI 資料（`@st.cache_data` 快取 30 分鐘）
- `get_city_aqi(all_data, city_en)` — 指定城市代表測站 AQI（同縣市多站取最高）
- `get_aqi_level(aqi)` — 回傳 (等級 i18n key, 顏色 hex)，6 級分類
- `get_all_cities_aqi(all_data)` — 12 城市 AQI 排行（降序）

## UV 指數分級

| UVI 範圍 | 等級 | 顏色 |
|----------|------|------|
| 0-2 | 低量 | #00e400 (green) |
| 3-5 | 中量 | #ffff00 (yellow) |
| 6-7 | 高量 | #ff7e00 (orange) |
| 8-10 | 過量 | #ff0000 (red) |
| 11+ | 危險 | #8f3f97 (purple) |

## 分享功能

- URL query params：`?city={city_en}&lang={lang}`
- `initialize_session_state()` 首次載入時讀取 `st.query_params` 設定城市 / 語言
- 即時天氣 tab 內提供分享 URL + 文字摘要 expander

## Tab 結構（共 8 個）

```
🏠 即時天氣 | 📊 預報圖表 | 📅 每日預報 | 🤖 AI分析 | ✈️ 旅遊推薦 | 🔄 城市比較 | 🌬️ 空氣品質 | 🗺️ 天氣地圖
```

## API Key 安全設計

| 優先順序 | 來源 | 說明 |
|----------|------|------|
| 1（最高） | sidebar 使用者輸入 | `st.session_state["sidebar_owm_key"]` / `sidebar_oai_key` / `sidebar_onecall_key` / `sidebar_aqi_key` |
| 2 | `.env` 檔案 | `config.get_env_api_key()` 於模組載入時讀取 |
| 3 | `st.secrets` | Streamlit Cloud 部署時由平台注入 |

**安全規則：**
- sidebar 輸入欄位 `value=""` — 永遠空白，不帶入 .env 的金鑰值
- 偵測到環境變數時只顯示「✅ 已從環境變數載入」狀態文字
- `.env` 已加入 `.gitignore`，不會上傳 GitHub

## AQI 分級配色

| AQI 範圍 | 等級 | 顏色 |
|----------|------|------|
| 0-50 | 良好 | #00e400 (green) |
| 51-100 | 普通 | #ffff00 (yellow) |
| 101-150 | 對敏感族群不健康 | #ff7e00 (orange) |
| 151-200 | 不健康 | #ff0000 (red) |
| 201-300 | 非常不健康 | #8f3f97 (purple) |
| 301+ | 危害 | #7e0023 (maroon) |

## 旅遊評分維度

| 維度 | 滿分 | 最佳範圍 | 扣分規則 |
|------|------|---------|---------|
| 溫度 | 40 | 18-26°C | 偏離每度扣 3 分 |
| 降雨 | 25 | 0% | 每 10% 扣 2.5 分 |
| 風速 | 15 | ≤5 m/s | >5 後每 1 m/s 扣 3 分 |
| 濕度 | 20 | 40-70% | 偏離每 5% 扣 2 分 |

## 規則引擎閾值參考

| 條件 | 觸發動作 |
|------|---------|
| 溫度 > 35°C | 高溫警告，避免戶外 |
| 溫度 > 33°C | 中暑風險提醒 |
| 溫度 > 30°C | 建議補水、清晨/傍晚運動 |
| 溫度 < 10°C | 低溫警告，心血管注意 |
| 溫度 < 15°C | 偏涼提醒，攜帶外套 |
| 降雨機率 > 60% | 必備雨具 |
| 降雨機率 > 30% | 建議帶傘 |
| 濕度 > 80% | 高濕悶熱，過敏提醒 |
| 濕度 < 30% | 乾燥保濕提醒 |
| 風速 > 10 m/s | 風大警告，避免山區 |
| 戶外適合條件 | 15°C ≤ 溫度 ≤ 33°C、降雨 < 60%、風速 < 10 |

## 穿搭溫度區間

| 區間 | 建議 |
|------|------|
| > 30°C | 短袖、短褲、防曬配件 |
| 25-30°C | 短袖/薄長袖、備薄外套 |
| 20-25°C | 長袖、薄外套 |
| 15-20°C | 長袖+毛衣、厚外套、圍巾 |
| < 15°C | 多層穿搭、羽絨衣、手套毛帽 |

## 部署

### 本地開發
```bash
uv sync && uv run streamlit run src/weather_analysis/app.py
```

### Streamlit Cloud
- **Main file path**: `src/weather_analysis/app.py`
- **依賴**: 自動讀取根目錄 `requirements.txt`
- **Secrets**: 在 Settings > Secrets 貼上：
  - `OPENWEATHER_API_KEY`（必填）
  - `OPENAI_API_KEY`（可選，GPT 分析）
  - `ONECALL_API_KEY`（可選，官方警報）
  - `AQI_API_KEY`（可選，空氣品質）

## 單元測試

```bash
uv run pytest tests/ -v       # 執行全部 99 個測試
```

測試覆蓋純邏輯模組（不需 Streamlit 環境）：
- `test_travel.py` — `score_day` 各維度 + 邊界值 + `recommend_best_days` 排序邏輯
- `test_aqi.py` — `get_aqi_level` 6 級分類 + `get_city_aqi` 多站取最高 + `get_all_cities_aqi` 排序
- `test_alerts.py` — `evaluate_alerts` 7 種警報類型 + 嚴重度互斥 + 邊界值 + 多重觸發
- `test_uv.py` — `get_uv_level` 5 級分類 + 邊界值

## 開發注意事項

- 所有模組使用 `from weather_analysis import config` / `from weather_analysis.xxx import Xxx` 絕對匯入
- `WeatherAPI.get_weather_icon_url()` 是 `@staticmethod`，在 app.py 中以類別名稱呼叫（不需實例）
- 所有 UI 字串必須使用 `t()` i18n 系統，不可硬編碼中文或英文
- Windows 終端機（cp950）無法顯示部分 emoji，但 Streamlit 瀏覽器中正常渲染
- 修改依賴後需執行 `uv sync` 並同步更新 `requirements.txt`
- visualization.py 中所有圖表方法皆為 `@staticmethod`，使用 `_get_plotly_template()` 適配深色模式
