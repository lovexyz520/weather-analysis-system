# 智慧天氣分析系統 — 系統規格書

## 專案概述

- **名稱**: weather-analysis-system（智慧天氣分析系統）
- **版本**: 1.0.0
- **語言**: Python 3.10+
- **框架**: Streamlit
- **用途**: 台灣 12 城市即時天氣查詢 + AI 智慧分析（GPT / 規則引擎）

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
        ├── app.py              # Streamlit 主程式（UI + 路由）
        ├── config.py           # 設定檔（API Key 載入 + 常數）
        ├── weather_api.py      # OpenWeatherMap API 整合
        ├── visualization.py    # Plotly 圖表生成（全部 @staticmethod）
        └── ai_analyzer.py      # AI 分析（GPT + 規則引擎 fallback）
```

## 模組職責

### config.py
- `get_env_api_key(key_name, placeholder)` — 統一 API Key 載入邏輯
  - 優先順序：`.env` 環境變數 → `st.secrets`（Streamlit Cloud）
  - 回傳空字串代表未設定
- 移除了 `ENABLE_AI_ANALYSIS` 旗標（AI 分析永遠可用，只是模式不同）
- `OPENAI_MODEL` = `gpt-4o-mini`
- 常數：`TAIWAN_CITIES`, `DEFAULT_CITY`, `FORECAST_DAYS`, `UNITS`, `LANG`, `AI_MAX_TOKENS`

### app.py
- **`_get_active_api_key(session_key, env_default)`** — 取得生效的 API Key
  - 優先順序：sidebar 使用者輸入（`st.session_state`）> `.env` / `st.secrets`
- **`display_sidebar()`** — 側邊欄結構：
  - 🔑 API Key 設定（兩個 password input，**欄位永遠空白**，不帶入 .env 值）
  - 偵測到 .env 時只顯示「✅ 已從環境變數載入」文字，不洩漏 Key 值
  - 城市選擇 → 更新按鈕 → 系統資訊
- **`fetch_weather_data(city)`** — 每次呼叫都用最新的 active key 建立 `WeatherAPI` 實例
- **`display_ai_analysis()`** — 永遠可用，不再阻擋
  - 有 OpenAI Key → 顯示「GPT 深度分析」
  - 無 OpenAI Key → 顯示「基礎規則分析」+ 升級提示
- CSS 樣式：`[data-testid="stMetric"]` 使用漸層紫色背景 + 白字，避免白底不可見

### weather_api.py
- `WeatherAPI` 類別：封裝 OpenWeatherMap API 呼叫
- `get_current_weather(city)` — 即時天氣（回傳 dict 或 None）
- `get_forecast(city)` — 5 天 / 每 3 小時預報（回傳 list 或 None）
- `get_daily_forecast_summary(city)` — 整理為每日摘要
- `get_weather_icon_url(icon_code)` — **@staticmethod**，app.py 以 `WeatherAPI.get_weather_icon_url()` 呼叫
- `_get_tw_city_name(city_en)` — 英文城市名轉中文

### visualization.py
- `WeatherCharts` 類別：全部為 **@staticmethod**
- `create_temperature_chart(forecast_data)` — 溫度趨勢折線圖
- `create_daily_summary_chart(daily_summary)` — 每日高低溫柱狀圖
- `create_humidity_rain_chart(forecast_data)` — 雙 Y 軸（濕度 + 降雨機率）
- `create_daily_pop_chart(daily_summary)` — 每日降雨機率（含背景色區域）
- `create_wind_speed_chart(forecast_data)` — 風速面積圖

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

## API Key 安全設計

| 優先順序 | 來源 | 說明 |
|----------|------|------|
| 1（最高） | sidebar 使用者輸入 | `st.session_state["sidebar_owm_key"]` / `sidebar_oai_key` |
| 2 | `.env` 檔案 | `config.get_env_api_key()` 於模組載入時讀取 |
| 3 | `st.secrets` | Streamlit Cloud 部署時由平台注入 |

**安全規則：**
- sidebar 輸入欄位 `value=""` — 永遠空白，不帶入 .env 的金鑰值
- 偵測到環境變數時只顯示「✅ 已從環境變數載入」狀態文字
- `.env` 已加入 `.gitignore`，不會上傳 GitHub

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
- **Secrets**: 在 Settings > Secrets 貼上 `OPENWEATHER_API_KEY` / `OPENAI_API_KEY`

## 開發注意事項

- 所有模組使用 `from weather_analysis import config` / `from weather_analysis.xxx import Xxx` 絕對匯入
- `WeatherAPI.get_weather_icon_url()` 是 `@staticmethod`，在 app.py 中以類別名稱呼叫（不需實例）
- Windows 終端機（cp950）無法顯示部分 emoji，但 Streamlit 瀏覽器中正常渲染
- 修改依賴後需執行 `uv sync` 並同步更新 `requirements.txt`
