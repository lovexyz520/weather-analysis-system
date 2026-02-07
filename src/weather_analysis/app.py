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
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


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

    st.sidebar.markdown("---")

    # ── 城市選擇 ──
    lang = get_lang()
    if lang == "zh_tw":
        city_display_list = list(config.TAIWAN_CITIES.keys())
        default_display = config.DEFAULT_CITY
    else:
        city_display_list = [config.TAIWAN_CITIES_I18N[en]["en"] for en in config.TAIWAN_CITIES.values()]
        default_display = "Taipei"

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
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🏠 {t('tab.current')}",
        f"📊 {t('tab.charts')}",
        f"📅 {t('tab.daily')}",
        f"🤖 {t('tab.ai')}",
    ])

    with tab1:
        display_current_weather()
    with tab2:
        display_forecast_charts()
    with tab3:
        display_daily_forecast_table()
    with tab4:
        display_ai_analysis()

    # 頁尾
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: var(--footer-color);'>
        <p>{t('app.footer')}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
