"""
智慧天氣分析系統 - Streamlit主程式
"""
import streamlit as st
from datetime import datetime
from weather_analysis import config
from weather_analysis.weather_api import WeatherAPI
from weather_analysis.visualization import WeatherCharts
from weather_analysis.ai_analyzer import WeatherAIAnalyzer
from weather_analysis.i18n import t, get_lang, weekday_name, SUPPORTED_LANGS
from weather_analysis.alerts import (
    evaluate_alerts, evaluate_onecall_alerts,
    AlertSeverity,
)
from weather_analysis.travel import recommend_best_days
from weather_analysis.aqi_api import (
    fetch_aqi_data, get_city_aqi, get_aqi_level, get_all_cities_aqi,
)
from weather_analysis.weather_api import _cached_onecall_uvi, get_uv_level

# 頁面設定
st.set_page_config(
    page_title="Smart Weather Analysis",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ── CSS 注入（深色模式 + RWD + 骨架屏） ──

def _inject_theme_css():
    """注入主題 CSS（含深色模式變數、RWD 規則、骨架屏動畫）"""
    st.markdown("""
    <style>
    /* ── CSS Custom Properties (Light) ── */
    :root {
        --header-color: #1E88E5;
        --card-gradient: linear-gradient(135deg, #667eea, #764ba2);
        --card-text: #ffffff;
        --card-highlight: #FFD93D;
        --ai-gradient: linear-gradient(135deg, #f093fb, #f5576c);
        --metric-shadow: rgba(0,0,0,0.1);
        --footer-color: #666;
        --skeleton-base: #e0e0e0;
        --skeleton-shine: #f0f0f0;
    }

    /* ── Dark mode overrides ── */
    [data-theme="dark"], .stApp[data-theme="dark"],
    html[data-theme="dark"], body[data-theme="dark"],
    .stApp.st-emotion-cache-dark {
        --header-color: #64B5F6;
        --card-gradient: linear-gradient(135deg, #4a5a8a, #5a3a7a);
        --ai-gradient: linear-gradient(135deg, #a050a8, #c04060);
        --metric-shadow: rgba(0,0,0,0.3);
        --footer-color: #999;
        --skeleton-base: #2a2a3a;
        --skeleton-shine: #3a3a4a;
    }

    /* Streamlit dark theme detection via prefers-color-scheme */
    @media (prefers-color-scheme: dark) {
        :root {
            --header-color: #64B5F6;
            --card-gradient: linear-gradient(135deg, #4a5a8a, #5a3a7a);
            --ai-gradient: linear-gradient(135deg, #a050a8, #c04060);
            --metric-shadow: rgba(0,0,0,0.3);
            --footer-color: #999;
            --skeleton-base: #2a2a3a;
            --skeleton-shine: #3a3a4a;
        }
    }

    /* ── Base styles ── */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--header-color);
        text-align: center;
        margin-bottom: 2rem;
    }
    .weather-card {
        background: var(--card-gradient);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: var(--card-text);
    }
    .weather-card h3 {
        color: var(--card-text);
        font-weight: bold;
    }
    .weather-card strong {
        color: var(--card-highlight);
    }
    .metric-card {
        background: var(--card-gradient);
        color: var(--card-text);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    [data-testid="stMetric"] {
        background: var(--card-gradient);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px var(--metric-shadow);
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: bold;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: var(--card-highlight) !important;
    }
    .ai-card {
        background: var(--ai-gradient);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: var(--card-text);
    }
    .ai-card h3 {
        color: var(--card-text);
        font-weight: bold;
        margin-bottom: 1rem;
    }

    /* ── Skeleton loading animation ── */
    @keyframes skeleton-shimmer {
        0%   { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }
    .skeleton {
        background: linear-gradient(90deg,
            var(--skeleton-base) 0%,
            var(--skeleton-shine) 50%,
            var(--skeleton-base) 100%);
        background-size: 200px 100%;
        animation: skeleton-shimmer 1.5s ease-in-out infinite;
        border-radius: 8px;
    }
    .skeleton-metric {
        height: 100px;
        margin-bottom: 0.5rem;
    }
    .skeleton-card {
        height: 180px;
        margin: 1rem 0;
    }
    .skeleton-chart {
        height: 400px;
        margin: 1rem 0;
    }

    /* ── RWD: Desktop / Mobile ── */
    @media (min-width: 769px) {
        .desktop-only { display: block; }
        .mobile-only  { display: none !important; }
    }
    @media (max-width: 768px) {
        .desktop-only { display: none !important; }
        .mobile-only  { display: block !important; }
        .main-header  { font-size: 1.8rem; }

        /* Streamlit columns 自動換行 */
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 1 1 100% !important; min-width: 100% !important;
        }
        /* metric 卡片 2×2 排列 */
        .metric-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 1 1 48% !important; min-width: 48% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# ── 工具函式 ──

def _get_active_api_key(session_key, env_default):
    """
    取得目前生效的 API Key
    優先順序：使用者在 sidebar 輸入 > .env / st.secrets
    """
    sidebar_val = st.session_state.get(session_key, "")
    return sidebar_val if sidebar_val else env_default


def initialize_session_state():
    """初始化session state"""
    defaults = {
        "current_weather": None,
        "forecast_data": None,
        "daily_summary": None,
        "ai_analysis": None,
        "last_city": None,
        "owm_validated": None,
        "owm_validated_key": "",
        "oai_validated": None,
        "oai_validated_key": "",
        "ui_lang": "zh_tw",
        "weather_alerts": [],
        "_query_params_applied": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # 從 URL query params 載入城市 / 語言（僅首次）
    if not st.session_state._query_params_applied:
        qp = st.query_params
        if "lang" in qp and qp["lang"] in ("zh_tw", "en"):
            st.session_state.ui_lang = qp["lang"]
        if "city" in qp:
            # city param 用英文城市名
            city_param = qp["city"]
            if city_param in config.TAIWAN_CITIES_COORDS:
                st.session_state["_share_city"] = city_param
        st.session_state._query_params_applied = True


def display_header():
    """顯示頁面標題"""
    st.markdown(f'<h1 class="main-header">🌤️ {t("app.header")}</h1>', unsafe_allow_html=True)
    st.markdown("---")


# ── 骨架屏 ──

def display_skeleton_loading():
    """顯示骨架屏（載入中佔位）"""
    # 4 個 metric 卡片骨架
    cols = st.columns(4)
    for col in cols:
        with col:
            st.markdown('<div class="skeleton skeleton-metric"></div>', unsafe_allow_html=True)
    # 天氣卡片骨架
    st.markdown('<div class="skeleton skeleton-card"></div>', unsafe_allow_html=True)


# ── 側邊欄 ──

def display_sidebar():
    """顯示側邊欄"""
    # ── 語言切換（最頂部） ──
    lang_options = list(SUPPORTED_LANGS.keys())
    lang_labels = list(SUPPORTED_LANGS.values())
    current_idx = lang_options.index(st.session_state.ui_lang) if st.session_state.ui_lang in lang_options else 0
    selected_label = st.sidebar.selectbox(
        t("sidebar.lang_label"),
        options=lang_labels,
        index=current_idx,
    )
    selected_lang = lang_options[lang_labels.index(selected_label)]
    if selected_lang != st.session_state.ui_lang:
        st.session_state.ui_lang = selected_lang
        # 清除快取以重新取得對應語言的天氣描述
        st.cache_data.clear()
        st.session_state.current_weather = None
        st.session_state.forecast_data = None
        st.session_state.daily_summary = None
        st.session_state.ai_analysis = None
        st.rerun()

    st.sidebar.title(f"⚙️ {t('sidebar.title')}")

    # ── API Key 設定 ──
    st.sidebar.subheader(f"🔑 {t('sidebar.api_key_section')}")

    # --- OpenWeatherMap API Key ---
    owm_env = config.OPENWEATHER_API_KEY
    st.sidebar.text_input(
        t("sidebar.owm_label"),
        value="",
        type="password",
        key="sidebar_owm_key",
        placeholder=t("sidebar.owm_placeholder"),
    )

    active_owm = _get_active_api_key("sidebar_owm_key", owm_env)
    sidebar_owm_input = st.session_state.get("sidebar_owm_key", "")

    if sidebar_owm_input:
        if sidebar_owm_input != st.session_state.owm_validated_key:
            ok, msg = WeatherAPI.validate_key(sidebar_owm_input)
            st.session_state.owm_validated = ok
            st.session_state.owm_validated_key = sidebar_owm_input
        if st.session_state.owm_validated:
            st.sidebar.caption(f"✅ {t('sidebar.owm_valid')}")
        else:
            st.sidebar.caption(f"❌ {t('sidebar.owm_invalid')}")
    elif owm_env:
        st.sidebar.caption(f"✅ {t('sidebar.owm_env_loaded')}")
    else:
        st.sidebar.caption(f"⚠️ {t('sidebar.owm_not_set')}")

    # --- OpenAI API Key（可選） ---
    oai_env = config.OPENAI_API_KEY
    st.sidebar.text_input(
        t("sidebar.oai_label"),
        value="",
        type="password",
        key="sidebar_oai_key",
        placeholder=t("sidebar.oai_placeholder"),
    )

    sidebar_oai_input = st.session_state.get("sidebar_oai_key", "")

    if sidebar_oai_input:
        if sidebar_oai_input != st.session_state.oai_validated_key:
            oai_ok = _validate_openai_key(sidebar_oai_input)
            st.session_state.oai_validated = oai_ok
            st.session_state.oai_validated_key = sidebar_oai_input
        if st.session_state.oai_validated:
            st.sidebar.caption(f"✅ {t('sidebar.oai_valid')}")
        else:
            st.sidebar.caption(f"❌ {t('sidebar.oai_invalid')}")
    elif oai_env:
        st.sidebar.caption(f"✅ {t('sidebar.oai_env_loaded')}")
    else:
        st.sidebar.caption(f"ℹ️ {t('sidebar.oai_not_set')}")

    # --- One Call API Key（可選） ---
    onecall_env = config.ONECALL_API_KEY
    st.sidebar.text_input(
        t("sidebar.onecall_label"),
        value="",
        type="password",
        key="sidebar_onecall_key",
        placeholder=t("sidebar.onecall_placeholder"),
    )

    sidebar_onecall_input = st.session_state.get("sidebar_onecall_key", "")
    if not sidebar_onecall_input and onecall_env:
        st.sidebar.caption(f"✅ {t('sidebar.onecall_env_loaded')}")
    elif not sidebar_onecall_input:
        st.sidebar.caption(f"ℹ️ {t('sidebar.onecall_not_set')}")

    # --- AQI API Key（可選） ---
    aqi_env = config.AQI_API_KEY
    st.sidebar.text_input(
        t("sidebar.aqi_label"),
        value="",
        type="password",
        key="sidebar_aqi_key",
        placeholder=t("sidebar.aqi_placeholder"),
    )

    sidebar_aqi_input = st.session_state.get("sidebar_aqi_key", "")
    if not sidebar_aqi_input and aqi_env:
        st.sidebar.caption(f"✅ {t('sidebar.aqi_env_loaded')}")
    elif not sidebar_aqi_input:
        st.sidebar.caption(f"ℹ️ {t('sidebar.aqi_not_set')}")

    st.sidebar.markdown("---")

    # ── 城市選擇 ──
    lang = get_lang()
    if lang == "zh_tw":
        city_display_list = list(config.TAIWAN_CITIES.keys())
        default_display = config.DEFAULT_CITY
    else:
        city_display_list = [config.TAIWAN_CITIES_I18N[en]["en"] for en in config.TAIWAN_CITIES.values()]
        default_display = "Taipei"

    # 從 URL query params 覆蓋預設城市
    share_city = st.session_state.pop("_share_city", None)
    if share_city:
        entry = config.TAIWAN_CITIES_I18N.get(share_city)
        if entry:
            default_display = entry.get(lang, default_display)

    default_idx = city_display_list.index(default_display) if default_display in city_display_list else 0

    city_display = st.sidebar.selectbox(
        t("sidebar.city_label"),
        options=city_display_list,
        index=default_idx,
    )

    # 轉換回英文城市名稱
    if lang == "zh_tw":
        city_en = config.TAIWAN_CITIES[city_display]
        city_tw = city_display
    else:
        # 從 en display name 找回英文 key
        city_en = city_display
        for en_key, names in config.TAIWAN_CITIES_I18N.items():
            if names["en"] == city_display:
                city_en = en_key
                break
        city_tw = city_display

    # 更新按鈕
    if st.sidebar.button(f"🔄 {t('sidebar.update_btn')}", type="primary", use_container_width=True):
        if not active_owm:
            st.sidebar.error(f"❌ {t('sidebar.no_owm_key')}")
        else:
            st.cache_data.clear()
            with st.spinner(t("app.loading_weather")):
                fetch_weather_data(city_en)
                st.success(f"✅ {t('app.data_updated')}")

    st.sidebar.markdown("---")

    # ── 系統資訊 ──
    st.sidebar.subheader(f"📊 {t('sidebar.sys_info')}")
    active_oai = _get_active_api_key("sidebar_oai_key", oai_env)
    ai_mode = f"🤖 {t('sidebar.ai_mode_gpt')}" if active_oai else f"📊 {t('sidebar.ai_mode_rule')}"

    city_display_name = WeatherAPI.get_city_display_name(city_en)
    st.sidebar.info(f"""
    **{t('sidebar.data_source')}**: OpenWeatherMap
    **{t('sidebar.current_city')}**: {city_display_name}
    **{t('sidebar.analysis_mode')}**: {ai_mode}
    **{t('sidebar.cache_time')}**: {t('sidebar.cache_minutes', n=config.CACHE_EXPIRE_MINUTES)}
    **{t('sidebar.update_time')}**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)

    return city_en, city_tw


def _validate_openai_key(api_key):
    """輕量驗證 OpenAI API Key"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        client.models.list()
        return True
    except Exception:
        return False


# ── 資料載入 ──

def fetch_weather_data(city):
    """取得天氣資料"""
    active_owm = _get_active_api_key("sidebar_owm_key", config.OPENWEATHER_API_KEY)
    api = WeatherAPI(api_key=active_owm)

    st.session_state.current_weather = api.get_current_weather(city)
    st.session_state.forecast_data = api.get_forecast(city)
    st.session_state.daily_summary = api.get_daily_forecast_summary(city)
    st.session_state.ai_analysis = None
    st.session_state.last_city = city

    # 計算天氣警報
    rule_alerts = evaluate_alerts(
        st.session_state.current_weather,
        st.session_state.daily_summary,
    )

    # One Call 官方警報
    active_onecall = _get_active_api_key("sidebar_onecall_key", config.ONECALL_API_KEY)
    onecall_alerts = []
    if active_onecall and city in config.TAIWAN_CITIES_COORDS:
        coords = config.TAIWAN_CITIES_COORDS[city]
        onecall_alerts = evaluate_onecall_alerts(active_onecall, coords["lat"], coords["lon"])

    st.session_state.weather_alerts = rule_alerts + onecall_alerts


# ── 天氣警報顯示 ──

def display_weather_alerts():
    """顯示天氣警報（header 下、tabs 上）"""
    alerts = st.session_state.get("weather_alerts", [])
    if not alerts:
        return

    st.subheader(f"⚠️ {t('alert.section_title')}")
    for alert in alerts:
        title = t(alert.title_key)
        # 官方警報使用 raw 文字
        if hasattr(alert, "_raw_event") and alert._raw_event:
            msg = f"**{alert._raw_event}**: {getattr(alert, '_raw_description', '')}"
        else:
            msg = t(alert.message_key, v=alert.value, t=alert.threshold)

        if alert.severity == AlertSeverity.DANGER:
            st.error(f"{alert.icon} **{title}** — {msg}")
        else:
            st.warning(f"{alert.icon} **{title}** — {msg}")


# ── 頁面顯示 ──

def display_current_weather():
    """顯示即時天氣"""
    weather = st.session_state.current_weather

    if not weather:
        st.info(f"👈 {t('app.no_data_hint')}")
        return

    st.subheader(f"📍 {t('current.title', city=weather['city_tw'])}")

    # metric 卡片外包 metric-row（RWD 2×2）
    st.markdown('<div class="metric-row">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=f"🌡️ {t('metric.temperature')}", value=f"{weather['temperature']}°C",
                  delta=t("metric.feels_like", v=weather['feels_like']))
    with col2:
        st.metric(label=f"💧 {t('metric.humidity')}", value=f"{weather['humidity']}%")
    with col3:
        st.metric(label=f"💨 {t('metric.wind_speed')}", value=f"{weather['wind_speed']} m/s")
    with col4:
        st.metric(label=f"☁️ {t('metric.clouds')}", value=f"{weather['clouds']}%")
    st.markdown('</div>', unsafe_allow_html=True)

    # 天氣狀況卡片
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 2])
    with col_left:
        icon_url = WeatherAPI.get_weather_icon_url(weather['icon'])
        st.image(icon_url, width=120)
    with col_right:
        st.markdown(f"""
        ### {weather['weather']}

        **{t('metric.temp_max')}**: {weather['temp_max']}°C | **{t('metric.temp_min')}**: {weather['temp_min']}°C
        **{t('metric.pressure')}**: {weather['pressure']} hPa
        **{t('metric.sunrise')}**: {weather['sunrise'].strftime('%H:%M')} | **{t('metric.sunset')}**: {weather['sunset'].strftime('%H:%M')}
        **{t('metric.data_time')}**: {weather['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 分享功能 ──
    # 組合完整 URL（自動偵測 Streamlit Cloud 或 localhost）
    import urllib.parse
    _base = st.context.headers.get("Host", "localhost:8501")
    _scheme = "https" if "streamlit.app" in _base or "share.streamlit.io" in _base else "http"
    _query = urllib.parse.urlencode({"city": weather["city"], "lang": get_lang()})
    share_url = f"{_scheme}://{_base}/?{_query}"

    summary_text = t("share.summary_template",
                     city=weather["city_tw"],
                     temp=weather["temperature"],
                     desc=weather["weather"],
                     feels=weather["feels_like"],
                     humidity=weather["humidity"],
                     wind=weather["wind_speed"])

    with st.expander(f"🔗 {t('share.title')}"):
        st.text_input(t("share.btn"), value=share_url, disabled=True)
        st.text_area(t("share.text_btn"), value=f"{summary_text}\n{share_url}", height=100)

    # ── UV 指數（需 One Call API Key） ──
    active_onecall = _get_active_api_key("sidebar_onecall_key", config.ONECALL_API_KEY)
    city_en = weather.get("city", "Taipei")
    if active_onecall and city_en in config.TAIWAN_CITIES_COORDS:
        coords = config.TAIWAN_CITIES_COORDS[city_en]
        uv_data = _cached_onecall_uvi(active_onecall, coords["lat"], coords["lon"])
        if uv_data:
            uvi = uv_data["uvi"]
            level_key, color = get_uv_level(uvi)
            level_text = t(level_key)

            # UV 建議
            if uvi <= 2:
                advice = t("uv.advice_low")
            elif uvi <= 5:
                advice = t("uv.advice_moderate")
            elif uvi <= 7:
                advice = t("uv.advice_high")
            elif uvi <= 10:
                advice = t("uv.advice_very_high")
            else:
                advice = t("uv.advice_extreme")

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}33, {color}11);
                        border-left: 5px solid {color};
                        padding: 1rem 1.5rem; border-radius: 10px; margin: 1rem 0;">
                <strong>☀️ {t('uv.title')}</strong>:
                <span style="font-size: 1.5rem; font-weight: bold; color: {color};">{uvi}</span>
                <span style="color: {color}; font-weight: bold;">({level_text})</span>
                <br><small>🛡️ {t('uv.protection')}: {advice}</small>
            </div>
            """, unsafe_allow_html=True)


def display_forecast_charts():
    """顯示預報圖表"""
    forecast_data = st.session_state.forecast_data
    daily_summary = st.session_state.daily_summary

    if not forecast_data or not daily_summary:
        st.warning(f"⚠️ {t('current.no_data')}")
        return

    st.markdown("---")
    st.subheader(f"📊 {t('forecast.title')}")

    st.plotly_chart(
        WeatherCharts.create_daily_summary_chart(daily_summary),
        use_container_width=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            WeatherCharts.create_temperature_chart(forecast_data),
            use_container_width=True
        )
    with col2:
        st.plotly_chart(
            WeatherCharts.create_daily_pop_chart(daily_summary),
            use_container_width=True
        )

    st.plotly_chart(
        WeatherCharts.create_humidity_rain_chart(forecast_data),
        use_container_width=True
    )
    st.plotly_chart(
        WeatherCharts.create_wind_speed_chart(forecast_data),
        use_container_width=True
    )

    # 熱力圖
    st.markdown("---")
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.plotly_chart(
            WeatherCharts.create_temp_heatmap(forecast_data),
            use_container_width=True,
        )
    with col_h2:
        st.plotly_chart(
            WeatherCharts.create_rain_heatmap(forecast_data),
            use_container_width=True,
        )


def display_daily_forecast_table():
    """顯示每日預報表格"""
    daily_summary = st.session_state.daily_summary

    if not daily_summary:
        return

    st.markdown("---")
    st.subheader(f"📅 {t('daily.title')}")

    lang = get_lang()

    # ── 桌面版：5 欄並排 ──
    st.markdown('<div class="desktop-only">', unsafe_allow_html=True)
    cols = st.columns(5)
    for idx, day in enumerate(daily_summary):
        with cols[idx]:
            if lang == "zh_tw":
                date_str = f"{day['date'].month}月{day['date'].day}日"
            else:
                date_str = day['date'].strftime('%m/%d')
            wd = weekday_name(day['date'].weekday())
            st.markdown(f"**{date_str}**")
            st.markdown(f"*{wd}*")
            icon_url = WeatherAPI.get_weather_icon_url(day['icon'])
            st.image(icon_url, width=80)
            st.markdown(f"""
            🌡️ {day['temp_min']}°C ~ {day['temp_max']}°C
            💧 {int(day['pop_max'])}%
            💨 {day['wind_speed_avg']} m/s
            {day['weather']}
            """)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 手機版：可展開的逐日卡片 ──
    st.markdown('<div class="mobile-only">', unsafe_allow_html=True)
    for day in daily_summary:
        if lang == "zh_tw":
            date_str = f"{day['date'].month}月{day['date'].day}日"
        else:
            date_str = day['date'].strftime('%m/%d')
        wd = weekday_name(day['date'].weekday())
        label = t("daily.expand_label",
                   date=date_str, weekday=wd,
                   tmin=day['temp_min'], tmax=day['temp_max'])
        with st.expander(label):
            icon_url = WeatherAPI.get_weather_icon_url(day['icon'])
            st.image(icon_url, width=60)
            st.markdown(f"""
            - 🌡️ {t('metric.temperature')}: {day['temp_min']}°C ~ {day['temp_max']}°C
            - 💧 {t('metric.rain_prob')}: {int(day['pop_max'])}%
            - 💨 {t('metric.wind_speed')}: {day['wind_speed_avg']} m/s
            - {day['weather']}
            """)
    st.markdown('</div>', unsafe_allow_html=True)


def display_ai_analysis():
    """顯示AI智慧分析"""
    current_weather = st.session_state.current_weather
    daily_summary = st.session_state.daily_summary

    if not current_weather or not daily_summary:
        st.warning(f"⚠️ {t('current.no_data')}")
        return

    active_oai = _get_active_api_key("sidebar_oai_key", config.OPENAI_API_KEY)
    if active_oai:
        st.subheader(f"🤖 {t('ai.subheader_gpt')}")
    else:
        st.subheader(f"📊 {t('ai.subheader_rule')}")
        st.caption(f"💡 {t('ai.upgrade_hint')}")

    st.markdown(f"**{t('ai.analysis_city')}**: {current_weather['city_tw']} | "
                f"**{t('ai.analysis_time')}**: {datetime.now().strftime('%H:%M:%S')}")

    button_label = f"🔮 {t('ai.btn_gpt')}" if active_oai else f"📊 {t('ai.btn_rule')}"
    if st.button(button_label, type="primary", use_container_width=True):
        ai_analyzer = WeatherAIAnalyzer(api_key=active_oai)
        # 骨架屏替代 spinner
        skeleton = st.empty()
        with skeleton.container():
            st.markdown('<div class="skeleton skeleton-card"></div>', unsafe_allow_html=True)
            st.markdown('<div class="skeleton skeleton-chart"></div>', unsafe_allow_html=True)
        st.session_state.ai_analysis = ai_analyzer.comprehensive_analysis(
            current_weather, daily_summary
        )
        skeleton.empty()

    if st.session_state.ai_analysis:
        analysis = st.session_state.ai_analysis
        mode = analysis.get("mode", "fallback")

        if mode == "gpt":
            st.success(f"🤖 {t('ai.result_gpt')}")
        else:
            st.info(f"📊 {t('ai.result_rule')}")

        tab1, tab2, tab3, tab4 = st.tabs([
            f"🧠 {t('ai.tab_weather')}",
            f"🎯 {t('ai.tab_activities')}",
            f"👔 {t('ai.tab_outfit')}",
            f"💪 {t('ai.tab_health')}",
        ])

        with tab1:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown(f"### 🧠 {t('ai.card_weather')}")
            st.markdown(analysis['weather_analysis'])
            st.markdown('</div>', unsafe_allow_html=True)
        with tab2:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown(f"### 🎯 {t('ai.card_activities')}")
            st.markdown(analysis['activities'])
            st.markdown('</div>', unsafe_allow_html=True)
        with tab3:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown(f"### 👔 {t('ai.card_outfit')}")
            st.markdown(analysis['outfit'])
            st.markdown('</div>', unsafe_allow_html=True)
        with tab4:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown(f"### 💪 {t('ai.card_health')}")
            st.markdown(analysis['health'])
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        mode_label = t("ai.report_mode_gpt") if mode == "gpt" else t("ai.report_mode_rule")
        analysis_text = f"""
{t('ai.report_title')}
================
{t('ai.report_city')}: {current_weather['city_tw']}
{t('ai.report_time')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{t('ai.report_mode')}: {mode_label}

【{t('ai.report_section_weather')}】
{analysis['weather_analysis']}

【{t('ai.report_section_activities')}】
{analysis['activities']}

【{t('ai.report_section_outfit')}】
{analysis['outfit']}

【{t('ai.report_section_health')}】
{analysis['health']}
"""
        st.download_button(
            label=f"📥 {t('ai.download_btn')}",
            data=analysis_text,
            file_name=f"weather_analysis_{current_weather['city_tw']}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )


# ── 旅遊推薦 ──

def display_travel_recommendation():
    """顯示旅遊最佳日推薦"""
    daily_summary = st.session_state.daily_summary

    if not daily_summary:
        st.warning(f"⚠️ {t('current.no_data')}")
        return

    st.subheader(f"✈️ {t('travel.title')}")
    st.caption(t('travel.subtitle'))

    results = recommend_best_days(daily_summary)
    if not results:
        return

    lang = get_lang()

    # 每日卡片
    cols = st.columns(len(results))
    for idx, day in enumerate(results):
        with cols[idx]:
            if lang == "zh_tw":
                date_str = f"{day['date'].month}月{day['date'].day}日"
            else:
                date_str = day['date'].strftime('%m/%d')
            wd = weekday_name(day['date'].weekday())

            # 推薦標章
            if day["recommended"]:
                st.markdown(f"⭐ **{t('travel.best_day')}**")

            st.markdown(f"**{date_str}** ({wd})")

            icon_url = WeatherAPI.get_weather_icon_url(day['icon'])
            st.image(icon_url, width=60)

            # 分數（顏色依分數高低）
            score = day["score"]
            if score >= 75:
                score_color = "🟢"
            elif score >= 50:
                score_color = "🟡"
            else:
                score_color = "🔴"
            st.markdown(f"{score_color} **{t('travel.score')}**: {score} {t('travel.score_unit')}")

            st.caption(t('travel.day_detail',
                         temp=day['temp_avg'],
                         pop=int(day['pop_max']),
                         wind=day['wind_speed_avg']))

            # 原因標籤
            for reason_key in day["reasons"]:
                st.markdown(f"- {t(reason_key)}")

    # 雷達圖：最佳日的維度細項
    st.markdown("---")
    best = max(results, key=lambda x: x["score"])
    if lang == "zh_tw":
        best_label = f"{best['date'].month}月{best['date'].day}日"
    else:
        best_label = best['date'].strftime('%m/%d')
    st.subheader(f"📊 {t('travel.radar_title')} — {best_label}")
    st.plotly_chart(
        WeatherCharts.create_travel_radar_chart(best["scores"]),
        use_container_width=True,
    )


# ── 多城市比較 ──

@st.fragment
def display_city_comparison():
    """顯示多城市天氣比較"""
    active_owm = _get_active_api_key("sidebar_owm_key", config.OPENWEATHER_API_KEY)
    if not active_owm:
        st.warning(f"⚠️ {t('compare.no_owm_key')}")
        return

    st.subheader(f"🔄 {t('compare.title')}")

    lang = get_lang()
    if lang == "zh_tw":
        city_options = list(config.TAIWAN_CITIES.keys())
    else:
        city_options = [config.TAIWAN_CITIES_I18N[en]["en"] for en in config.TAIWAN_CITIES.values()]

    selected = st.multiselect(
        t('compare.select_label'),
        options=city_options,
        default=city_options[:2],
        max_selections=4,
        help=t('compare.select_hint'),
    )

    if len(selected) < 2:
        st.info(f"ℹ️ {t('compare.need_more')}")
        return

    # 把顯示名轉回英文城市名
    selected_en = []
    for name in selected:
        if lang == "zh_tw":
            selected_en.append(config.TAIWAN_CITIES[name])
        else:
            for en_key, names in config.TAIWAN_CITIES_I18N.items():
                if names["en"] == name:
                    selected_en.append(en_key)
                    break

    # 取得各城市資料
    api = WeatherAPI(api_key=active_owm)
    city_data_list = []
    for city_en in selected_en:
        daily = api.get_daily_forecast_summary(city_en)
        if daily:
            display_name = WeatherAPI.get_city_display_name(city_en)
            city_data_list.append({
                "city": display_name,
                "daily_summary": daily,
            })

    if len(city_data_list) < 2:
        st.warning(f"⚠️ {t('current.no_data')}")
        return

    st.plotly_chart(
        WeatherCharts.create_comparison_temp_chart(city_data_list),
        use_container_width=True,
    )
    st.plotly_chart(
        WeatherCharts.create_comparison_rain_chart(city_data_list),
        use_container_width=True,
    )


# ── 空氣品質 ──

def display_aqi():
    """顯示空氣品質 AQI"""
    active_aqi = _get_active_api_key("sidebar_aqi_key", config.AQI_API_KEY)
    if not active_aqi:
        st.info(f"ℹ️ {t('aqi.no_key')}")
        return

    st.subheader(f"🌬️ {t('aqi.title')}")

    all_data = fetch_aqi_data(active_aqi)
    if not all_data:
        st.warning(f"⚠️ {t('aqi.no_data')}")
        return

    # 當前城市 AQI
    city_en = st.session_state.get("last_city", "Taipei")
    city_info = get_city_aqi(all_data, city_en)
    city_display = WeatherAPI.get_city_display_name(city_en)

    if city_info:
        level_key, color = get_aqi_level(city_info["aqi"])
        level_text = t(level_key)

        # 大卡片
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}33, {color}11);
                    border-left: 5px solid {color};
                    padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="margin:0;">{t('aqi.current_city', city=city_display)}</h2>
            <div style="font-size: 3rem; font-weight: bold; color: {color};">{city_info['aqi']}</div>
            <div style="font-size: 1.2rem; color: {color}; font-weight: bold;">{level_text}</div>
            <div style="margin-top: 0.5rem;">
                📍 {t('aqi.station')}: {city_info['station']}
                {"| 🏭 " + t('aqi.pollutant') + ": " + city_info['pollutant'] if city_info['pollutant'] else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PM2.5, PM10, O3 metrics
        st.markdown('<div class="metric-row">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            pm25 = city_info['pm25']
            st.metric(t('aqi.pm25'), f"{pm25}" if pm25 is not None else "N/A")
        with c2:
            pm10 = city_info['pm10']
            st.metric(t('aqi.pm10'), f"{pm10}" if pm10 is not None else "N/A")
        with c3:
            o3 = city_info['o3']
            st.metric(t('aqi.o3'), f"{o3}" if o3 is not None else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)

    # 12 城市 AQI 排行
    st.markdown("---")
    st.subheader(f"📊 {t('aqi.ranking_title')}")

    all_cities = get_all_cities_aqi(all_data)
    if all_cities:
        rows = []
        for info in all_cities:
            lk, lc = get_aqi_level(info["aqi"])
            display = WeatherAPI.get_city_display_name(info["city_en"])
            rows.append({
                t('aqi.ranking_city'): display,
                t('aqi.ranking_aqi'): info["aqi"],
                t('aqi.ranking_level'): t(lk),
                t('aqi.ranking_station'): info["station"],
            })

        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── 天氣地圖 ──

def display_weather_map():
    """顯示互動式天氣地圖"""
    active_owm = _get_active_api_key("sidebar_owm_key", config.OPENWEATHER_API_KEY)
    if not active_owm:
        st.warning(f"⚠️ {t('map.no_owm_key')}")
        return

    st.subheader(f"🗺️ {t('map.title')}")

    import folium
    from streamlit_folium import st_folium

    # 建立台灣中心地圖
    m = folium.Map(location=[23.5, 121], zoom_start=7, tiles="OpenStreetMap")

    # 收集各城市天氣資料
    api = WeatherAPI(api_key=active_owm)

    # AQI 資料（如有 key）
    active_aqi = _get_active_api_key("sidebar_aqi_key", config.AQI_API_KEY)
    aqi_data = None
    if active_aqi:
        aqi_data = fetch_aqi_data(active_aqi)

    has_data = False
    for city_en, coords in config.TAIWAN_CITIES_COORDS.items():
        weather = api.get_current_weather(city_en)
        if not weather:
            continue
        has_data = True

        temp = weather["temperature"]
        city_name = weather["city_tw"]
        desc = weather["weather"]
        humidity = weather["humidity"]
        wind = weather["wind_speed"]

        # 溫度分級顏色
        if temp >= 35:
            color = "#FF0000"
        elif temp >= 30:
            color = "#FF6B6B"
        elif temp >= 25:
            color = "#FFA500"
        elif temp >= 20:
            color = "#4ECDC4"
        elif temp >= 15:
            color = "#45B7D1"
        else:
            color = "#6C5CE7"

        # popup 內容
        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 150px;">
            <h4 style="margin:0 0 5px 0;">{city_name}</h4>
            <b>{t('map.popup_temp')}</b>: {temp}°C<br>
            <b>{t('map.popup_weather')}</b>: {desc}<br>
            <b>{t('map.popup_humidity')}</b>: {humidity}%<br>
            <b>{t('map.popup_wind')}</b>: {wind} m/s
        """

        # 加入 AQI（如有）
        if aqi_data:
            city_aqi = get_city_aqi(aqi_data, city_en)
            if city_aqi:
                aqi_level_key, aqi_color = get_aqi_level(city_aqi["aqi"])
                popup_html += f"""<br><b>{t('map.popup_aqi')}</b>:
                    <span style="color:{aqi_color}; font-weight:bold;">{city_aqi['aqi']} ({t(aqi_level_key)})</span>"""

        popup_html += "</div>"

        folium.CircleMarker(
            location=[coords["lat"], coords["lon"]],
            radius=12,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{city_name} {temp}°C",
        ).add_to(m)

    if not has_data:
        st.info(f"ℹ️ {t('map.no_data')}")
        return

    st_folium(m, width=None, height=500, returned_objects=[])


# ── 主程式 ──

def main():
    """主程式"""
    initialize_session_state()
    _inject_theme_css()
    display_header()

    city_en, city_tw = display_sidebar()

    # 偵測城市切換 → 自動刷新
    active_owm = _get_active_api_key("sidebar_owm_key", config.OPENWEATHER_API_KEY)
    city_changed = st.session_state.last_city is not None and st.session_state.last_city != city_en
    first_load = st.session_state.current_weather is None

    if active_owm and (first_load or city_changed):
        # 骨架屏載入
        skeleton = st.empty()
        with skeleton.container():
            display_skeleton_loading()
        fetch_weather_data(city_en)
        skeleton.empty()

    # 天氣警報（在 tabs 上方）
    display_weather_alerts()

    # 主要內容區域
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        f"🏠 {t('tab.current')}",
        f"📊 {t('tab.charts')}",
        f"📅 {t('tab.daily')}",
        f"🤖 {t('tab.ai')}",
        f"✈️ {t('tab.travel')}",
        f"🔄 {t('tab.compare')}",
        f"🌬️ {t('tab.aqi')}",
        f"🗺️ {t('tab.map')}",
    ])

    with tab1:
        display_current_weather()
    with tab2:
        display_forecast_charts()
    with tab3:
        display_daily_forecast_table()
    with tab4:
        display_ai_analysis()
    with tab5:
        display_travel_recommendation()
    with tab6:
        display_city_comparison()
    with tab7:
        display_aqi()
    with tab8:
        display_weather_map()

    # 頁尾
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: var(--footer-color);'>
        <p>{t('app.footer')}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
