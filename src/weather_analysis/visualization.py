"""
視覺化模組 - 使用Plotly生成互動式圖表
"""
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime
from collections import defaultdict
from weather_analysis.i18n import t, weekday_name


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

    @staticmethod
    def create_comparison_temp_chart(city_data_list):
        """
        多城市溫度比較折線圖。

        Args:
            city_data_list: [{"city": str, "daily_summary": list[dict]}, ...]
        """
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        fig = go.Figure()

        for idx, item in enumerate(city_data_list):
            city_name = item["city"]
            daily = item["daily_summary"]
            dates = [d["date"].strftime("%m/%d") for d in daily]
            temps = [d["temp_avg"] for d in daily]
            color = colors[idx % len(colors)]

            fig.add_trace(go.Scatter(
                x=dates,
                y=temps,
                mode='lines+markers',
                name=city_name,
                line=dict(color=color, width=3),
                marker=dict(size=8),
            ))

        fig.update_layout(
            title=t('chart.compare_temp'),
            xaxis_title=t('chart.date'),
            yaxis_title=t('chart.temp_unit'),
            hovermode='x unified',
            template=_get_plotly_template(),
            height=450,
        )

        return fig

    @staticmethod
    def create_comparison_rain_chart(city_data_list):
        """
        多城市降雨機率比較柱狀圖 (grouped bar)。

        Args:
            city_data_list: [{"city": str, "daily_summary": list[dict]}, ...]
        """
        colors = ['#6C5CE7', '#00B894', '#FDCB6E', '#E17055', '#74B9FF']
        fig = go.Figure()

        for idx, item in enumerate(city_data_list):
            city_name = item["city"]
            daily = item["daily_summary"]
            dates = [d["date"].strftime("%m/%d") for d in daily]
            pops = [d["pop_max"] for d in daily]
            color = colors[idx % len(colors)]

            fig.add_trace(go.Bar(
                x=dates,
                y=pops,
                name=city_name,
                marker_color=color,
                text=[f"{int(p)}%" for p in pops],
                textposition='outside',
            ))

        fig.update_layout(
            title=t('chart.compare_rain'),
            xaxis_title=t('chart.date'),
            yaxis_title=t('chart.rain_unit'),
            hovermode='x unified',
            template=_get_plotly_template(),
            height=450,
            barmode='group',
        )

        return fig

    @staticmethod
    def create_travel_radar_chart(scores: dict):
        """
        旅遊評分雷達圖。

        Args:
            scores: {"temp_score": float, "rain_score": float,
                     "wind_score": float, "humidity_score": float}
        """
        categories = [
            t('travel.dim_temp'),
            t('travel.dim_rain'),
            t('travel.dim_wind'),
            t('travel.dim_humidity'),
        ]
        # 歸一化到 0-100
        values = [
            scores["temp_score"] / 40 * 100,
            scores["rain_score"] / 25 * 100,
            scores["wind_score"] / 15 * 100,
            scores["humidity_score"] / 20 * 100,
        ]
        # 閉合雷達圖
        values.append(values[0])
        categories.append(categories[0])

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(102, 126, 234, 0.25)',
            line=dict(color='#667eea', width=2),
            name=t('travel.score'),
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
            ),
            template=_get_plotly_template(),
            height=350,
            showlegend=False,
        )

        return fig

    @staticmethod
    def create_temp_heatmap(forecast_data):
        """
        溫度熱力圖：X=時段, Y=日期, Z=溫度。

        Args:
            forecast_data: 3 小時制預報資料 list[dict]
        """
        grid = defaultdict(dict)
        dates_set = set()
        for item in forecast_data:
            dt = item["datetime"]
            date_label = f"{dt.month:02d}/{dt.day:02d} ({weekday_name(dt.weekday())})"
            hour_label = f"{dt.hour:02d}:00"
            grid[date_label][hour_label] = item["temperature"]
            dates_set.add(date_label)

        dates = sorted(dates_set, key=lambda d: d)
        hours = sorted({f"{h:02d}:00" for item in forecast_data for h in [item["datetime"].hour]})

        z = []
        for date in dates:
            row = [grid[date].get(h, None) for h in hours]
            z.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=hours,
            y=dates,
            colorscale="RdYlBu_r",
            text=[[f"{v}°C" if v is not None else "" for v in row] for row in z],
            texttemplate="%{text}",
            hovertemplate="%{y} %{x}<br>%{z}°C<extra></extra>",
            colorbar=dict(title="°C"),
        ))

        fig.update_layout(
            title=t("chart.heatmap_temp_title"),
            xaxis_title=t("chart.heatmap_hour"),
            yaxis_title=t("chart.heatmap_date"),
            yaxis=dict(autorange="reversed"),
            template=_get_plotly_template(),
            height=350,
        )

        return fig

    @staticmethod
    def create_rain_heatmap(forecast_data):
        """
        降雨機率熱力圖：X=時段, Y=日期, Z=降雨機率%。

        Args:
            forecast_data: 3 小時制預報資料 list[dict]
        """
        grid = defaultdict(dict)
        dates_set = set()
        for item in forecast_data:
            dt = item["datetime"]
            date_label = f"{dt.month:02d}/{dt.day:02d} ({weekday_name(dt.weekday())})"
            hour_label = f"{dt.hour:02d}:00"
            grid[date_label][hour_label] = item["pop"]
            dates_set.add(date_label)

        dates = sorted(dates_set, key=lambda d: d)
        hours = sorted({f"{h:02d}:00" for item in forecast_data for h in [item["datetime"].hour]})

        z = []
        for date in dates:
            row = [grid[date].get(h, None) for h in hours]
            z.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=hours,
            y=dates,
            colorscale=[[0, "#00e400"], [0.3, "#ffff00"], [0.6, "#ff7e00"], [1, "#ff0000"]],
            zmin=0,
            zmax=100,
            text=[[f"{int(v)}%" if v is not None else "" for v in row] for row in z],
            texttemplate="%{text}",
            hovertemplate="%{y} %{x}<br>%{z}%<extra></extra>",
            colorbar=dict(title="%"),
        ))

        fig.update_layout(
            title=t("chart.heatmap_rain_title"),
            xaxis_title=t("chart.heatmap_hour"),
            yaxis_title=t("chart.heatmap_date"),
            yaxis=dict(autorange="reversed"),
            template=_get_plotly_template(),
            height=350,
        )

        return fig
