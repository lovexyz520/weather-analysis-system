"""
視覺化模組 - 使用Plotly生成互動式圖表
"""
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

class WeatherCharts:
    """天氣圖表生成類別"""
    
    @staticmethod
    def create_temperature_chart(forecast_data):
        """
        創建溫度趨勢圖
        
        Args:
            forecast_data: 預報資料列表
            
        Returns:
            plotly.graph_objects.Figure: 圖表物件
        """
        dates = [item['datetime'] for item in forecast_data]
        temps = [item['temperature'] for item in forecast_data]
        feels_like = [item['feels_like'] for item in forecast_data]
        
        fig = go.Figure()
        
        # 實際溫度線
        fig.add_trace(go.Scatter(
            x=dates,
            y=temps,
            mode='lines+markers',
            name='實際溫度',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8)
        ))
        
        # 體感溫度線
        fig.add_trace(go.Scatter(
            x=dates,
            y=feels_like,
            mode='lines+markers',
            name='體感溫度',
            line=dict(color='#4ECDC4', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='溫度趨勢預報',
            xaxis_title='日期時間',
            yaxis_title='溫度 (°C)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_daily_summary_chart(daily_summary):
        """
        創建每日天氣摘要圖表
        
        Args:
            daily_summary: 每日摘要資料
            
        Returns:
            plotly.graph_objects.Figure: 圖表物件
        """
        dates = [item['date'].strftime('%m/%d') for item in daily_summary]
        temp_max = [item['temp_max'] for item in daily_summary]
        temp_min = [item['temp_min'] for item in daily_summary]
        temp_avg = [item['temp_avg'] for item in daily_summary]
        
        fig = go.Figure()
        
        # 最高溫度
        fig.add_trace(go.Bar(
            x=dates,
            y=temp_max,
            name='最高溫',
            marker_color='#FF6B6B',
            text=[f"{t}°C" for t in temp_max],
            textposition='outside'
        ))
        
        # 平均溫度
        fig.add_trace(go.Scatter(
            x=dates,
            y=temp_avg,
            name='平均溫',
            mode='lines+markers',
            line=dict(color='#FFA500', width=3),
            marker=dict(size=10)
        ))
        
        # 最低溫度
        fig.add_trace(go.Bar(
            x=dates,
            y=temp_min,
            name='最低溫',
            marker_color='#4ECDC4',
            text=[f"{t}°C" for t in temp_min],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='未來5天溫度預報',
            xaxis_title='日期',
            yaxis_title='溫度 (°C)',
            hovermode='x unified',
            template='plotly_white',
            height=450,
            barmode='group'
        )
        
        return fig
    
    @staticmethod
    def create_humidity_rain_chart(forecast_data):
        """
        創建濕度與降雨機率圖表
        
        Args:
            forecast_data: 預報資料列表
            
        Returns:
            plotly.graph_objects.Figure: 圖表物件
        """
        dates = [item['datetime'] for item in forecast_data]
        humidity = [item['humidity'] for item in forecast_data]
        pop = [item['pop'] for item in forecast_data]
        
        fig = go.Figure()
        
        # 濕度線（左Y軸）
        fig.add_trace(go.Scatter(
            x=dates,
            y=humidity,
            name='濕度',
            mode='lines+markers',
            line=dict(color='#95E1D3', width=2),
            yaxis='y'
        ))
        
        # 降雨機率柱狀圖（右Y軸）
        fig.add_trace(go.Bar(
            x=dates,
            y=pop,
            name='降雨機率',
            marker_color='#6C5CE7',
            opacity=0.6,
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='濕度與降雨機率預報',
            xaxis_title='日期時間',
            yaxis=dict(
                title='濕度 (%)',
                side='left'
            ),
            yaxis2=dict(
                title='降雨機率 (%)',
                side='right',
                overlaying='y'
            ),
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_daily_pop_chart(daily_summary):
        """
        創建每日降雨機率圖表
        
        Args:
            daily_summary: 每日摘要資料
            
        Returns:
            plotly.graph_objects.Figure: 圖表物件
        """
        dates = [item['date'].strftime('%m/%d') for item in daily_summary]
        pop = [item['pop_max'] for item in daily_summary]
        
        # 根據降雨機率設定顏色
        colors = ['#95E1D3' if p < 30 else '#FFD93D' if p < 60 else '#FF6B6B' for p in pop]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates,
            y=pop,
            marker_color=colors,
            text=[f"{int(p)}%" for p in pop],
            textposition='outside',
            name='降雨機率'
        ))
        
        fig.update_layout(
            title='未來5天降雨機率',
            xaxis_title='日期',
            yaxis_title='降雨機率 (%)',
            template='plotly_white',
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
        """
        創建風速圖表
        
        Args:
            forecast_data: 預報資料列表
            
        Returns:
            plotly.graph_objects.Figure: 圖表物件
        """
        dates = [item['datetime'] for item in forecast_data]
        wind_speed = [item['wind_speed'] for item in forecast_data]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=wind_speed,
            mode='lines+markers',
            name='風速',
            line=dict(color='#74B9FF', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(116, 185, 255, 0.2)'
        ))
        
        fig.update_layout(
            title='風速預報',
            xaxis_title='日期時間',
            yaxis_title='風速 (m/s)',
            hovermode='x unified',
            template='plotly_white',
            height=350
        )
        
        return fig
