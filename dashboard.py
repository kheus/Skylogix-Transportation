# dashboard.py - SkyLogix Weather Dashboard
import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SkyLogix Weather Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# Title and description
st.title("🌤️ SkyLogix Transportation - Real-Time Weather Dashboard")
st.markdown("""
Monitoring weather conditions across SkyLogix operational cities to optimize logistics and ensure driver safety.
""")

# Database connection function
def get_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(os.getenv('POSTGRES_URI', 'postgresql://postgres:Cheikh12@localhost/postgres'))

# Load data with caching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_current_weather():
    """Load current weather for all cities"""
    conn = get_connection()
    query = """
    SELECT city, country, temp_c, feels_like_c, condition_main, 
           condition_description, wind_speed_ms, humidity_pct, 
           pressure_hpa, cloud_pct, observed_at,
           CASE 
               WHEN wind_speed_ms > 10 THEN 'High Wind'
               WHEN rain_1h_mm > 5 THEN 'Heavy Rain'
               WHEN temp_c > 35 THEN 'Extreme Heat'
               WHEN temp_c < 5 THEN 'Extreme Cold'
               ELSE 'Normal'
           END as alert_level
    FROM weather_readings 
    WHERE observed_at = (
        SELECT MAX(observed_at) 
        FROM weather_readings wr2 
        WHERE wr2.city = weather_readings.city
    )
    ORDER BY city
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_historical_data(hours=24):
    """Load historical data for trends"""
    conn = get_connection()
    query = f"""
    SELECT city, observed_at, temp_c, humidity_pct, 
           wind_speed_ms, pressure_hpa, rain_1h_mm
    FROM weather_readings 
    WHERE observed_at >= NOW() - INTERVAL '{hours} hours'
    ORDER BY observed_at
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=3600)
def load_summary_data(days=7):
    """Load summary data for the past N days"""
    conn = get_connection()
    query = f"""
    SELECT 
        city,
        ROUND(AVG(temp_c), 1) as avg_temp,
        ROUND(AVG(humidity_pct), 0) as avg_humidity,
        MAX(wind_speed_ms) as max_wind,
        SUM(rain_1h_mm) as total_rain,
        COUNT(CASE WHEN condition_main LIKE '%%Rain%%' THEN 1 END) as rainy_days,
        COUNT(*) as total_readings
    FROM weather_readings 
    WHERE observed_at >= NOW() - INTERVAL '{days} days'
    GROUP BY city
    ORDER BY city
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load data
current_data = load_current_weather()
historical_data = load_historical_data(24)
summary_data = load_summary_data(7)

# Sidebar filters
st.sidebar.header("Dashboard Filters")
selected_cities = st.sidebar.multiselect(
    "Select Cities",
    options=current_data['city'].unique().tolist(),
    default=current_data['city'].unique().tolist()[:4]
)

time_range = st.sidebar.selectbox(
    "Time Range for Trends",
    options=["Last 6 hours", "Last 24 hours", "Last 3 days"],
    index=1
)

# Convert time range to hours
hours_map = {"Last 6 hours": 6, "Last 24 hours": 24, "Last 3 days": 72}
hours = hours_map[time_range]
filtered_historical = historical_data[historical_data['observed_at'] >= 
                                     datetime.now() - timedelta(hours=hours)]
filtered_historical = filtered_historical[filtered_historical['city'].isin(selected_cities)]

# Main dashboard layout
tab1, tab2, tab3, tab4 = st.tabs(["Current Conditions", "Trends", "Alerts", "Analytics"])

# Tab 1: Current Conditions
with tab1:
    st.header("Current Weather Conditions")
    
    if not selected_cities:
        st.warning("Please select at least one city from the sidebar.")
    else:
        # Create metrics cards
        cols = st.columns(len(selected_cities))
        
        for idx, city in enumerate(selected_cities):
            city_data = current_data[current_data['city'] == city]
            if not city_data.empty:
                with cols[idx]:
                    data = city_data.iloc[0]
                    
                    # Temperature metric
                    st.metric(
                        label=f"**{city}** ({data['country']})",
                        value=f"{data['temp_c']:.1f}°C",
                        delta=f"Feels like {data['feels_like_c']:.1f}°C"
                    )
                    
                    # Condition badge
                    condition_color = {
                        'Clear': '🟢', 'Clouds': '⛅', 'Rain': '🌧️',
                        'Snow': '❄️', 'Thunderstorm': '⛈️', 'Drizzle': '🌦️'
                    }.get(data['condition_main'], '☀️')
                    
                    st.write(f"{condition_color} **{data['condition_main']}**")
                    st.write(f"*{data['condition_description']}*")
                    
                    # Details
                    st.write("---")
                    st.write(f"**Wind:** {data['wind_speed_ms']} m/s")
                    st.write(f"**Humidity:** {data['humidity_pct']}%")
                    st.write(f"**Pressure:** {data['pressure_hpa']} hPa")
                    st.write(f"**Clouds:** {data['cloud_pct']}%")
                    st.write(f"**Last Updated:** {data['observed_at'].strftime('%H:%M')}")

# Tab 2: Trends
with tab2:
    st.header("Weather Trends")
    
    if filtered_historical.empty:
        st.info("No historical data available for the selected cities and time range.")
    else:
        # Temperature trends
        st.subheader("Temperature Trends")
        fig_temp = px.line(
            filtered_historical, 
            x='observed_at', 
            y='temp_c', 
            color='city',
            title=f'Temperature Over Time ({time_range})',
            labels={'observed_at': 'Time', 'temp_c': 'Temperature (°C)', 'city': 'City'}
        )
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Humidity trends
        st.subheader("Humidity Trends")
        cols = st.columns(2)
        
        with cols[0]:
            fig_humidity = px.line(
                filtered_historical, 
                x='observed_at', 
                y='humidity_pct', 
                color='city',
                title='Humidity Over Time',
                labels={'observed_at': 'Time', 'humidity_pct': 'Humidity (%)'}
            )
            st.plotly_chart(fig_humidity, use_container_width=True)
        
        with cols[1]:
            fig_wind = px.line(
                filtered_historical, 
                x='observed_at', 
                y='wind_speed_ms', 
                color='city',
                title='Wind Speed Over Time',
                labels={'observed_at': 'Time', 'wind_speed_ms': 'Wind Speed (m/s)'}
            )
            st.plotly_chart(fig_wind, use_container_width=True)

# Tab 3: Alerts
with tab3:
    st.header("Weather Alerts")
    
    # Get alerts (conditions that might affect operations)
    alerts_data = current_data[current_data['alert_level'] != 'Normal']
    
    if alerts_data.empty:
        st.success("✅ No weather alerts - All conditions are normal for operations.")
    else:
        st.warning(f"⚠️ **{len(alerts_data)} Active Alert(s)**")
        
        for _, alert in alerts_data.iterrows():
            alert_color = {
                'High Wind': '🟡',
                'Heavy Rain': '🔵', 
                'Extreme Heat': '🔴',
                'Extreme Cold': '🟣'
            }.get(alert['alert_level'], '⚪')
            
            st.markdown(f"""
            {alert_color} **{alert['city']} - {alert['alert_level']}**
            - Temperature: {alert['temp_c']:.1f}°C
            - Wind Speed: {alert['wind_speed_ms']} m/s
            - Condition: {alert['condition_main']}
            - Time: {alert['observed_at'].strftime('%Y-%m-%d %H:%M')}
            ---
            """)
    
    # Logistics impact
    st.subheader("Logistics Impact Assessment")
    st.markdown("""
    **How weather affects SkyLogix operations:**
    
    - **High Wind (>10 m/s)**: Delay departures, avoid high-profile vehicles on bridges
    - **Heavy Rain (>5 mm/hr)**: Add 30% to delivery time estimates, avoid flooded routes
    - **Extreme Heat (>35°C)**: Schedule breaks for drivers, monitor refrigeration units
    - **Extreme Cold (<5°C)**: Check vehicle antifreeze, watch for icy roads
    
    **Recommended Actions:**
    1. Check the Alerts tab regularly
    2. Adjust delivery SLAs based on conditions
    3. Communicate with drivers about hazardous conditions
    4. Update insurance risk assessments
    """)

# Tab 4: Analytics
with tab4:
    st.header("Analytics & Reports")
    
    # Summary table
    st.subheader("7-Day Weather Summary")
    if not summary_data.empty:
        # Format the summary table
        display_summary = summary_data.copy()
        display_summary.columns = [
            'City', 'Avg Temp (°C)', 'Avg Humidity (%)', 
            'Max Wind (m/s)', 'Total Rain (mm)', 'Rainy Days', 'Total Readings'
        ]
        st.dataframe(display_summary, use_container_width=True)
    
    # Sample analytics queries
    st.subheader("Sample Analytics Queries")
    
    with st.expander("View SQL Queries for Analysis"):
        st.code("""
        -- 1. Weather trends per city (daily averages)
        SELECT 
            city,
            DATE(observed_at) as date,
            ROUND(AVG(temp_c), 1) as avg_temp,
            ROUND(AVG(humidity_pct), 0) as avg_humidity,
            MAX(wind_speed_ms) as max_wind
        FROM weather_readings 
        WHERE observed_at >= NOW() - INTERVAL '30 days'
        GROUP BY city, DATE(observed_at)
        ORDER BY date DESC, city;
        
        -- 2. Extreme condition detection
        SELECT 
            city,
            COUNT(*) as extreme_events,
            SUM(CASE WHEN wind_speed_ms > 10 THEN 1 ELSE 0 END) as high_wind_events,
            SUM(CASE WHEN rain_1h_mm > 5 THEN 1 ELSE 0 END) as heavy_rain_events,
            SUM(CASE WHEN temp_c > 35 THEN 1 ELSE 0 END) as extreme_heat_events
        FROM weather_readings 
        WHERE observed_at >= NOW() - INTERVAL '7 days'
        GROUP BY city
        ORDER BY extreme_events DESC;
        
        -- 3. Integration with logistics data (example)
        -- Assuming a 'deliveries' table exists:
        SELECT 
            d.delivery_id,
            d.estimated_time,
            d.actual_time,
            w.temp_c,
            w.condition_main,
            w.wind_speed_ms,
            CASE 
                WHEN w.rain_1h_mm > 5 THEN 'Delayed - Heavy Rain'
                WHEN w.wind_speed_ms > 10 THEN 'Delayed - High Winds'
                ELSE 'On Time'
            END as delay_reason
        FROM deliveries d
        JOIN weather_readings w 
            ON d.destination_city = w.city 
            AND w.observed_at BETWEEN d.start_time - INTERVAL '1 hour' 
                                 AND d.start_time + INTERVAL '1 hour';
        """, language='sql')
    
    # Data freshness indicator
    st.subheader("Data Pipeline Status")
    if not current_data.empty:
        latest_update = current_data['observed_at'].max()
        time_diff = (datetime.now() - latest_update).total_seconds() / 60  # minutes
        
        if time_diff < 30:
            st.success(f"✅ Data is fresh. Last update: {latest_update.strftime('%Y-%m-%d %H:%M')} ({time_diff:.0f} minutes ago)")
        elif time_diff < 120:
            st.warning(f"⚠️ Data may be stale. Last update: {latest_update.strftime('%Y-%m-%d %H:%M')} ({time_diff:.0f} minutes ago)")
        else:
            st.error(f"❌ Data pipeline may be down. Last update: {latest_update.strftime('%Y-%m-%d %H:%M')} ({time_diff:.0f} minutes ago)")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("""
**SkyLogix Weather Pipeline**
- Last Updated: Automatically every 15 minutes
- Data Source: OpenWeatherMap API
- Storage: MongoDB (raw), PostgreSQL (analytics)
- Dashboard: Streamlit
""")

# Auto-refresh
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Add auto-refresh every 5 minutes
st.sidebar.markdown("*Auto-refreshes every 5 minutes*")

if __name__ == "__main__":
    # This ensures the script runs properly
    pass