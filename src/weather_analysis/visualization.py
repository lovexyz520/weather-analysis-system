"""
視覺化模組 - 使用Plotly生成互動式圖表
"""
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime
from weather_analysis.i18n import t


def _get_plotly_template():
    """根據 Streamlit 主題返回 Plotly 模板"""
    try:
        theme = st.get_option("theme.base")
        if theme == "dark":
            return "plotly_dark"
    except Exception:
        pass
    return "plotly_white"


class WeatherCharts:
    """天氣圖表生成類別"""

    @staticmethod
    def create_temperature_chart(forecast_data):
        """創建溫度趨勢圖"""
        dates = [item['datetime'] for item in forecast_data]
        temps = [item['temperature'] for item in forecast_data]
        feels_like = [item['feels_like'] for item in forecast_data]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=temps,
            mode='lines+markers',
            name=t('chart.actual_temp'),
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=dates,
            y=feels_like,
            mode='lines+markers',
            name=t('chart.feels_like'),
            line=dict(color='#4ECDC4', width=2, dash='dash'),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title=t('chart.temp_trend'),
            xaxis_title=t('chart.datetime'),
            yaxis_title=t('chart.temp_unit'),
            hovermode='x unified',
            template=_get_plotly_template(),
            height=400
        )

        return fig

    @staticmethod
    def create_daily_summary_chart(daily_summary):
        """創建每日天氣摘要圖表"""
        dates = [item['date'].strftime('%m/%d') for item in daily_summary]
        temp_max = [item['temp_max'] for item in daily_summary]
        temp_min = [item['temp_min'] for item in daily_summary]
        temp_avg = [item['temp_avg'] for item in daily_summary]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=dates,
            y=temp_max,
            name=t('chart.temp_max'),
            marker_color='#FF6B6B',
            text=[f"{t_val}°C" for t_val in temp_max],
            textposition='outside'
        ))

        fig.add_trace(go.Scatter(
            x=dates,
            y=temp_avg,
            name=t('chart.temp_avg'),
            mode='lines+markers',
            line=dict(color='#FFA500', width=3),
            marker=dict(size=10)
        ))

        fig.add_trace(go.Bar(
            x=dates,
            y=temp_min,
            name=t('chart.temp_min'),
            marker_color='#4ECDC4',
            text=[f"{t_val}°C" for t_val in temp_min],
            textposition='outside'
        ))

        fig.update_layout(
            title=t('chart.daily_summary'),
            xaxis_title=t('chart.date'),
            yaxis_title=t('chart.temp_unit'),
            hovermode='x unified',
            template=_get_plotly_template(),
            height=450,
            barmode='group'
        )

        return fig

    @staticmethod
    def create_humidity_rain_chart(forecast_data):
        """創建濕度與降雨機率圖表"""
        dates = [item['datetime'] for item in forecast_data]
        humidity = [item['humidity'] for item in forecast_data]
        pop = [item['pop'] for item in forecast_data]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=humidity,
            name=t('chart.humidity'),
            mode='lines+markers',
            line=dict(color='#95E1D3', width=2),
            yaxis='y'
        ))

        fig.add_trace(go.Bar(
            x=dates,
            y=pop,
            name=t('chart.rain_prob'),
            marker_color='#6C5CE7',
            opacity=0.6,
            yaxis='y2'
        ))

        fig.update_layout(
            title=t('chart.humidity_rain'),
            xaxis_title=t('chart.datetime'),
            yaxis=dict(
                title=t('chart.humidity_unit'),
                side='left'
            ),
            yaxis2=dict(
                title=t('chart.rain_unit'),
                side='right',
                overlaying='y'
            ),
            hovermode='x unified',
            template=_get_plotly_template(),
            height=400
        )

        return fig

    @staticmethod
    def create_daily_pop_chart(daily_summary):
        """創建每日降雨機率圖表"""
        dates = [item['date'].strftime('%m/%d') for item in daily_summary]
        pop = [item['pop_max'] for item in daily_summary]

        colors = ['#95E1D3' if p < 30 else '#FFD93D' if p < 60 else '#FF6B6B' for p in pop]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=dates,
            y=pop,
            marker_color=colors,
            text=[f"{int(p)}%" for p in pop],
            textposition='outside',
            name=t('chart.rain_prob')
        ))

        fig.update_layout(
            title=t('chart.daily_pop'),
            xaxis_title=t('chart.date'),
            yaxis_title=t('chart.rain_unit'),
            template=_get_plotly_template(),
            height=400,
            showlegend=False
        )

        # 添加背景色區域
        fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, line_width=0)
        fig.add_hrect(y0=30, y1=60, fillcolor="yellow", opacity=0.1, line_width=0)
        fig.add_hrect(y0=60, y1=100, fillcolor="red", opacity=0.1, line_width=0)

        return fig

    @staticmethod
    def create_wind_speed_chart(forecast_data):
        """創建風速圖表"""
        dates = [item['datetime'] for item in forecast_data]
        wind_speed = [item['wind_speed'] for item in forecast_data]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=wind_speed,
            mode='lines+markers',
            name=t('chart.wind'),
            line=dict(color='#74B9FF', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(116, 185, 255, 0.2)'
        ))

        fig.update_layout(
            title=t('chart.wind_speed'),
            xaxis_title=t('chart.datetime'),
            yaxis_title=t('chart.wind_unit'),
            hovermode='x unified',
            template=_get_plotly_template(),
            height=350
        )

        return fig
