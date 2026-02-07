"""
智慧天氣分析系統 - Streamlit主程式
"""
import streamlit as st
from datetime import datetime
from weather_analysis import config
from weather_analysis.weather_api import WeatherAPI
from weather_analysis.visualization import WeatherCharts
from weather_analysis.ai_analyzer import WeatherAIAnalyzer

# 頁面設定
st.set_page_config(
    page_title="智慧天氣分析系統",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂CSS樣式
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    .weather-card h3 {
        color: white;
        font-weight: bold;
    }
    .weather-card strong {
        color: #FFD93D;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
        color: #FFD93D !important;
    }
    .ai-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    .ai-card h3 {
        color: white;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def _get_active_api_key(session_key, env_default):
    """
    取得目前生效的 API Key
    優先順序：使用者在 sidebar 輸入 > .env / st.secrets
    """
    sidebar_val = st.session_state.get(session_key, "")
    return sidebar_val if sidebar_val else env_default


def initialize_session_state():
    """初始化session state"""
    if 'current_weather' not in st.session_state:
        st.session_state.current_weather = None
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None
    if 'daily_summary' not in st.session_state:
        st.session_state.daily_summary = None
    if 'ai_analysis' not in st.session_state:
        st.session_state.ai_analysis = None


def display_header():
    """顯示頁面標題"""
    st.markdown('<h1 class="main-header">🌤️ 智慧天氣分析系統</h1>', unsafe_allow_html=True)
    st.markdown("---")


def display_sidebar():
    """顯示側邊欄"""
    st.sidebar.title("⚙️ 系統設定")

    # ── API Key 設定 ──
    st.sidebar.subheader("🔑 API Key 設定")

    # OpenWeatherMap API Key — 欄位永遠空白，不帶入 .env 值
    owm_env = config.OPENWEATHER_API_KEY
    st.sidebar.text_input(
        "OpenWeatherMap API Key",
        value="",
        type="password",
        key="sidebar_owm_key",
        placeholder="輸入 API Key（或由環境變數自動載入）",
    )
    if owm_env:
        st.sidebar.caption("✅ 已從環境變數載入（如需覆蓋請在上方輸入）")
    else:
        st.sidebar.caption("⚠️ 未偵測到環境變數，請在上方輸入 API Key")

    # OpenAI API Key（可選）— 欄位永遠空白
    oai_env = config.OPENAI_API_KEY
    st.sidebar.text_input(
        "OpenAI API Key（可選）",
        value="",
        type="password",
        key="sidebar_oai_key",
        placeholder="輸入 API Key 啟用 GPT 深度分析",
    )
    if oai_env:
        st.sidebar.caption("✅ 已從環境變數載入 (GPT 模式)")
    else:
        st.sidebar.caption("ℹ️ 未設定（將使用基礎規則分析）")

    st.sidebar.markdown("---")

    # ── 城市選擇 ──
    city_tw = st.sidebar.selectbox(
        "選擇城市",
        options=list(config.TAIWAN_CITIES.keys()),
        index=list(config.TAIWAN_CITIES.keys()).index(config.DEFAULT_CITY)
    )

    city_en = config.TAIWAN_CITIES[city_tw]

    # 取得目前生效的 API Key
    active_owm = _get_active_api_key("sidebar_owm_key", owm_env)

    # 更新按鈕
    if st.sidebar.button("🔄 更新天氣資料", type="primary", use_container_width=True):
        if not active_owm:
            st.sidebar.error("❌ 請先輸入 OpenWeatherMap API Key")
        else:
            with st.spinner("正在載入天氣資料..."):
                fetch_weather_data(city_en)
                st.success("✅ 資料更新成功！")

    st.sidebar.markdown("---")

    # ── 系統資訊 ──
    st.sidebar.subheader("📊 系統資訊")

    active_oai = _get_active_api_key("sidebar_oai_key", oai_env)
    ai_mode = "🤖 GPT 深度分析" if active_oai else "📊 基礎規則分析"

    st.sidebar.info(f"""
    **資料來源**: OpenWeatherMap
    **當前城市**: {city_tw}
    **分析模式**: {ai_mode}
    **更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)

    return city_en, city_tw


def fetch_weather_data(city):
    """取得天氣資料"""
    active_owm = _get_active_api_key("sidebar_owm_key", config.OPENWEATHER_API_KEY)
    api = WeatherAPI(api_key=active_owm)

    # 取得即時天氣
    st.session_state.current_weather = api.get_current_weather(city)

    # 取得預報資料
    st.session_state.forecast_data = api.get_forecast(city)

    # 取得每日摘要
    st.session_state.daily_summary = api.get_daily_forecast_summary(city)

    # 切換城市/key 時清除舊的 AI 分析
    st.session_state.ai_analysis = None


def display_current_weather():
    """顯示即時天氣"""
    weather = st.session_state.current_weather

    if not weather:
        st.info("👈 請在側邊欄輸入 OpenWeatherMap API Key 並點擊「更新天氣資料」")
        return

    st.subheader(f"📍 {weather['city_tw']} 即時天氣")

    # 使用欄位布局
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🌡️ 溫度",
            value=f"{weather['temperature']}°C",
            delta=f"體感 {weather['feels_like']}°C"
        )

    with col2:
        st.metric(
            label="💧 濕度",
            value=f"{weather['humidity']}%"
        )

    with col3:
        st.metric(
            label="💨 風速",
            value=f"{weather['wind_speed']} m/s"
        )

    with col4:
        st.metric(
            label="☁️ 雲量",
            value=f"{weather['clouds']}%"
        )

    # 天氣狀況卡片
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2])

    with col_left:
        # 顯示天氣圖示
        icon_url = WeatherAPI.get_weather_icon_url(weather['icon'])
        st.image(icon_url, width=120)

    with col_right:
        st.markdown(f"""
        ### {weather['weather']}

        **最高溫**: {weather['temp_max']}°C | **最低溫**: {weather['temp_min']}°C
        **氣壓**: {weather['pressure']} hPa
        **日出**: {weather['sunrise'].strftime('%H:%M')} | **日落**: {weather['sunset'].strftime('%H:%M')}
        **資料時間**: {weather['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
        """)

    st.markdown('</div>', unsafe_allow_html=True)


def display_forecast_charts():
    """顯示預報圖表"""
    forecast_data = st.session_state.forecast_data
    daily_summary = st.session_state.daily_summary

    if not forecast_data or not daily_summary:
        st.warning("⚠️ 無預報資料")
        return

    st.markdown("---")
    st.subheader("📊 天氣預報分析")

    # 每日摘要圖表
    st.plotly_chart(
        WeatherCharts.create_daily_summary_chart(daily_summary),
        use_container_width=True
    )

    # 兩欄布局
    col1, col2 = st.columns(2)

    with col1:
        # 溫度趨勢
        st.plotly_chart(
            WeatherCharts.create_temperature_chart(forecast_data),
            use_container_width=True
        )

    with col2:
        # 降雨機率
        st.plotly_chart(
            WeatherCharts.create_daily_pop_chart(daily_summary),
            use_container_width=True
        )

    # 濕度與降雨
    st.plotly_chart(
        WeatherCharts.create_humidity_rain_chart(forecast_data),
        use_container_width=True
    )

    # 風速
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
    st.subheader("📅 未來5天天氣預報")

    # 建立表格數據
    cols = st.columns(5)

    for idx, day in enumerate(daily_summary):
        with cols[idx]:
            # 顯示日期
            st.markdown(f"**{day['date'].strftime('%m月%d日')}**")
            st.markdown(f"*{['一','二','三','四','五','六','日'][day['date'].weekday()]}*")

            # 天氣圖示
            icon_url = WeatherAPI.get_weather_icon_url(day['icon'])
            st.image(icon_url, width=80)

            # 天氣資訊
            st.markdown(f"""
            🌡️ {day['temp_min']}°C ~ {day['temp_max']}°C
            💧 {int(day['pop_max'])}%
            💨 {day['wind_speed_avg']} m/s
            {day['weather']}
            """)


def display_ai_analysis():
    """顯示AI智慧分析"""
    current_weather = st.session_state.current_weather
    daily_summary = st.session_state.daily_summary

    if not current_weather or not daily_summary:
        st.warning("⚠️ 請先更新天氣資料")
        return

    # 判斷分析模式
    active_oai = _get_active_api_key("sidebar_oai_key", config.OPENAI_API_KEY)
    if active_oai:
        st.subheader("🤖 AI智慧分析（GPT 深度分析）")
    else:
        st.subheader("📊 AI智慧分析（基礎規則分析）")
        st.caption("💡 輸入 OpenAI API Key 可升級為 GPT 深度分析模式")

    st.markdown(f"**分析城市**: {current_weather['city_tw']} | **分析時間**: {datetime.now().strftime('%H:%M:%S')}")

    # 生成分析按鈕
    button_label = "🔮 生成 GPT 深度分析" if active_oai else "📊 生成基礎規則分析"
    if st.button(button_label, type="primary", use_container_width=True):
        ai_analyzer = WeatherAIAnalyzer(api_key=active_oai)
        with st.spinner("正在分析天氣資料中..."):
            st.session_state.ai_analysis = ai_analyzer.comprehensive_analysis(
                current_weather,
                daily_summary
            )

    # 顯示分析結果
    if st.session_state.ai_analysis:
        analysis = st.session_state.ai_analysis

        # 顯示分析模式標記
        mode = analysis.get("mode", "fallback")
        if mode == "gpt":
            st.success("🤖 以下為 GPT 深度分析結果")
        else:
            st.info("📊 以下為基礎規則分析結果（輸入 OpenAI Key 可升級）")

        # 創建4個分頁
        tab1, tab2, tab3, tab4 = st.tabs([
            "🧠 天氣分析",
            "🎯 活動建議",
            "👔 穿搭建議",
            "💪 健康建議"
        ])

        with tab1:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown("### 🧠 專業天氣分析")
            st.markdown(analysis['weather_analysis'])
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown("### 🎯 個人化活動建議")
            st.markdown(analysis['activities'])
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown("### 👔 智慧穿搭建議")
            st.markdown(analysis['outfit'])
            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown("### 💪 健康照護建議")
            st.markdown(analysis['health'])
            st.markdown('</div>', unsafe_allow_html=True)

        # 下載分析結果
        st.markdown("---")
        analysis_text = f"""
智慧天氣分析報告
================
城市: {current_weather['city_tw']}
分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析模式: {"GPT 深度分析" if mode == "gpt" else "基礎規則分析"}

【天氣分析】
{analysis['weather_analysis']}

【活動建議】
{analysis['activities']}

【穿搭建議】
{analysis['outfit']}

【健康建議】
{analysis['health']}
"""
        st.download_button(
            label="📥 下載分析報告",
            data=analysis_text,
            file_name=f"weather_analysis_{current_weather['city_tw']}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )


def main():
    """主程式"""
    # 初始化
    initialize_session_state()

    # 顯示標題
    display_header()

    # 顯示側邊欄並取得選擇的城市
    city_en, city_tw = display_sidebar()

    # 檢查是否需要載入初始資料
    active_owm = _get_active_api_key("sidebar_owm_key", config.OPENWEATHER_API_KEY)
    if st.session_state.current_weather is None and active_owm:
        with st.spinner(f"正在載入 {city_tw} 的天氣資料..."):
            fetch_weather_data(city_en)

    # 主要內容區域
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 即時天氣",
        "📊 預報圖表",
        "📅 每日預報",
        "🤖 AI智慧分析"
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
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>智慧天氣分析系統 v1.0.0 | 資料來源: OpenWeatherMap | AI: OpenAI GPT / 規則引擎 |
        Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
