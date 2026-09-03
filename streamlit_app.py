import streamlit as st
import streamlit.components.v1 as components
import folium
import requests
import datetime
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from streamlit_folium import st_folium

# --- ÖKOBAUDAT-STYLE DATABASE ---
# Metrics based on typical EPD (Environmental Product Declaration) data.
# u_value: W/m2K (approximate based on standard thickness)
# absorptance: solar absorptance (0-1)
# density: kg/m3
# embodied_energy: MJ/kg
# gwp (Global Warming Potential): kg CO2-eq/kg (negative means carbon sink)
MATERIALS = {
    "Concrete (Standard)": {"u_value": 2.0, "absorptance": 0.6, "density": 2400, "embodied_energy": 1.0, "gwp": 0.15, "cost_per_kg": 0.10},
    "Concrete (Aerated)": {"u_value": 0.3, "absorptance": 0.5, "density": 600, "embodied_energy": 3.0, "gwp": 0.3, "cost_per_kg": 0.30},
    "Brick (Solid)": {"u_value": 1.8, "absorptance": 0.7, "density": 1900, "embodied_energy": 3.0, "gwp": 0.22, "cost_per_kg": 0.15},
    "Brick (Hollow)": {"u_value": 1.2, "absorptance": 0.7, "density": 1300, "embodied_energy": 2.5, "gwp": 0.2, "cost_per_kg": 0.12},
    "Wood (Softwood)": {"u_value": 0.13, "absorptance": 0.8, "density": 500, "embodied_energy": 8.0, "gwp": -1.5, "cost_per_kg": 0.50}, 
    "Wood (Hardwood)": {"u_value": 0.16, "absorptance": 0.8, "density": 700, "embodied_energy": 10.0, "gwp": -1.2, "cost_per_kg": 1.20},
    "Steel (Galvanized)": {"u_value": 50.0, "absorptance": 0.4, "density": 7800, "embodied_energy": 35.0, "gwp": 2.8, "cost_per_kg": 1.50},
    "Aluminum (Sheet)": {"u_value": 205.0, "absorptance": 0.3, "density": 2700, "embodied_energy": 170.0, "gwp": 8.5, "cost_per_kg": 4.00},
    "Adobe / Mudbrick": {"u_value": 1.2, "absorptance": 0.65, "density": 1700, "embodied_energy": 0.5, "gwp": 0.05, "cost_per_kg": 0.02},
    "Rammed Earth": {"u_value": 1.5, "absorptance": 0.65, "density": 2000, "embodied_energy": 0.4, "gwp": 0.04, "cost_per_kg": 0.05},
    "Straw Bale": {"u_value": 0.07, "absorptance": 0.7, "density": 110, "embodied_energy": 0.2, "gwp": -2.0, "cost_per_kg": 0.10},
    "SIPs (Insulated Panels)": {"u_value": 0.25, "absorptance": 0.5, "density": 300, "embodied_energy": 45.0, "gwp": 2.5, "cost_per_kg": 2.00},
    "Stone (Granite/Marble)": {"u_value": 3.0, "absorptance": 0.6, "density": 2600, "embodied_energy": 2.0, "gwp": 0.1, "cost_per_kg": 1.00},
    "Bamboo": {"u_value": 0.15, "absorptance": 0.6, "density": 600, "embodied_energy": 3.0, "gwp": -1.8, "cost_per_kg": 0.30}
}

st.set_page_config(page_title="Shelter Analyzer & 3D Design", layout="wide")

# --- PURE CSS ENHANCEMENTS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Page title / H1 */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        color: var(--text-color) !important;
        margin-bottom: 0.8rem !important;
    }

    h2, h3, h4 {
        font-weight: 700 !important;
        color: var(--text-color) !important;
        letter-spacing: -0.02em !important;
    }

    /* Modern Card style for Metrics */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        border-color: var(--primary-color);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: var(--text-color) !important;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: var(--text-color) !important;
        font-size: 1.7rem !important;
    }

    /* Polished Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.4rem !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.35) !important;
        filter: brightness(1.05);
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--secondary-background-color);
        padding: 6px;
        border-radius: 12px;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-color);
        opacity: 0.7;
        background-color: transparent;
        border: none !important;
        padding: 0 20px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        opacity: 1;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }

    /* Alerts and Notification Boxes */
    div[data-testid="stAlert"] {
        border-radius: 12px;
        border-width: 1px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
        padding: 14px 18px;
    }

    /* Dataframe and Tables */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    /* Input elements & select boxes */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 10px !important;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
    }

    /* Dividers */
    hr {
        margin: 2rem 0 !important;
        border: 0 !important;
        height: 1px !important;
        background: linear-gradient(90deg, rgba(128,128,128,0) 0%, rgba(128,128,128,0.3) 50%, rgba(128,128,128,0) 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Shelter Weather Analyzer & 3D Thermodynamics")

tab1, tab2, tab3 = st.tabs(["1. Map & Weather Data", "2. 3D Design & Thermodynamics", "3. 3D Building Simulation"])

# --- TAB 1: Map & Weather ---
with tab1:
    st.write("Click on the map to pinpoint a location, then click **Analyze Weather**.")
    col1, col2 = st.columns([2, 1])

    with col1:
        if "lat" not in st.session_state:
            st.session_state.lat = 20.5937
        if "lon" not in st.session_state:
            st.session_state.lon = 78.9629

        m = folium.Map(
            location=[st.session_state.lat, st.session_state.lon], 
            zoom_start=5,
            tiles="https://mt1.google.com/vt/lyrs=m&gl=IN&hl=en-IN&x={x}&y={y}&z={z}",
            attr="Google Maps (India)"
        )
        
        folium.Marker(
            [st.session_state.lat, st.session_state.lon],
            popup="Selected Location",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
        # We capture clicks using st_folium, but disable the annoying LatLngPopup
        st_data = st_folium(m, height=500, width=800)

    with col2:
        st.subheader("Location Selection")
        
        if "lat" not in st.session_state:
            st.session_state.lat = 20.5937
        if "lon" not in st.session_state:
            st.session_state.lon = 78.9629
        if "last_map_click" not in st.session_state:
            st.session_state.last_map_click = None
            
        if st_data and st_data.get("last_clicked") and st_data.get("last_clicked") != st.session_state.last_map_click:
            st.session_state.last_map_click = st_data["last_clicked"]
            st.session_state.lat = st_data["last_clicked"]["lat"]
            st.session_state.lon = st_data["last_clicked"]["lng"]
            st.rerun()
            
        lat = st.number_input("Latitude", value=float(st.session_state.lat), format="%.4f", step=0.1)
        lon = st.number_input("Longitude", value=float(st.session_state.lon), format="%.4f", step=0.1)
        
        st.session_state.lat = lat
        st.session_state.lon = lon
        
        st.subheader("Data Range")
        default_start = datetime.date(2016, 1, 1)
        default_end = datetime.date.today() - datetime.timedelta(days=7)
        start_date = st.date_input("Start Date", default_start)
        end_date = st.date_input("End Date", default_end)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        if st.button("Analyze Weather", type="primary"):
            with st.spinner(f"Fetching historical data ({start_date_str} to {end_date_str})..."):
                url = "https://archive-api.open-meteo.com/v1/archive"
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,soil_temperature_0_to_7cm_mean,soil_moisture_0_to_7cm_mean,relative_humidity_2m_mean,shortwave_radiation_sum",
                    "timezone": "auto"
                }
                try:
                    response = requests.get(url, params=params)
                    data = response.json()
                    
                    if "daily" not in data:
                        st.error("Could not fetch data for this location.")
                    else:
                        daily = data["daily"]
                        t_max = [v for v in daily.get("temperature_2m_max", []) if v is not None]
                        t_min = [v for v in daily.get("temperature_2m_min", []) if v is not None]
                        precip = [v for v in daily.get("precipitation_sum", []) if v is not None]
                        solar = [v for v in daily.get("shortwave_radiation_sum", []) if v is not None]
                        wind = [v for v in daily.get("wind_speed_10m_max", []) if v is not None]
                        hum = [v for v in daily.get("relative_humidity_2m_mean", []) if v is not None]
                        soil_t = [v for v in daily.get("soil_temperature_0_to_7cm_mean", []) if v is not None]
                        soil_m = [v for v in daily.get("soil_moisture_0_to_7cm_mean", []) if v is not None]
                        
                        avg_t_max = sum(t_max) / len(t_max) if t_max else 0
                        avg_t_min = sum(t_min) / len(t_min) if t_min else 0
                        avg_solar = sum(solar) / len(solar) if solar else 0
                        
                        ext_max = max(t_max) if t_max else 0
                        ext_min = min(t_min) if t_min else 0
                        max_wind = max(wind) if wind else 0
                        avg_wind = sum(wind) / len(wind) if wind else 0
                        avg_hum = sum(hum) / len(hum) if hum else 0
                        avg_soil_t = sum(soil_t) / len(soil_t) if soil_t else 0
                        avg_soil_m = sum(soil_m) / len(soil_m) if soil_m else 0
                        
                        max_daily_precip = max(precip) if precip else 0
                        years_of_data = len(precip) / 365.25 if precip else 1
                        total_precip_per_year = sum(precip) / years_of_data if precip else 0
                        
                        st.session_state.weather_data = {
                            "avg_temp": (avg_t_max + avg_t_min) / 2,
                            "avg_solar_mj": avg_solar,
                            "ext_max": ext_max,
                            "ext_min": ext_min,
                            "avg_wind": avg_wind,
                            "is_cold": avg_t_min < 10,
                            "is_hot": avg_t_max > 30,
                            "lat": lat
                        }
                        
                        st.success("Weather data loaded! Go to the '3D Design & Thermodynamics' tab.")
                        
                        st.subheader(f"Weather Dashboard ({start_date_str[:4]} - {end_date_str[:4]})")
                        st.write(f"**Avg Max Temp:** {avg_t_max:.1f}°C")
                        st.write(f"**Avg Min Temp:** {avg_t_min:.1f}°C")
                        st.write(f"**Extreme Max Temp:** {ext_max:.1f}°C")
                        st.write(f"**Extreme Min Temp:** {ext_min:.1f}°C")
                        st.write(f"**Avg Humidity:** {avg_hum:.1f}%")
                        st.write(f"**Max Wind Speed:** {max_wind:.1f} km/h (Avg: {avg_wind:.1f} km/h)")
                        st.write(f"**Avg Daily Solar Radiance:** {avg_solar:.2f} MJ/m²")
                        st.write(f"**Avg Soil Temp (0-7cm):** {avg_soil_t:.1f}°C")
                        st.write(f"**Avg Soil Moisture:** {avg_soil_m:.3f} m³/m³")
                        st.write(f"**Avg Yearly Precip:** {total_precip_per_year:.1f} mm")
                        
                        st.subheader("Shelter Build Analysis")
                        if ext_max > 35:
                            st.warning("🔥 Extreme Heat Detected! Shelter needs significant cooling/ventilation and heat insulation.")
                        elif avg_t_max > 25:
                            st.info("☀️ Warm Climate. Good ventilation is recommended.")
                            
                        if ext_min < 0:
                            st.error("❄️ Freezing Temperatures! Shelter MUST have heating and thick insulation to prevent pipes freezing.")
                        elif avg_t_min < 10:
                            st.info("🧥 Cold Climate. Basic heating and insulation needed.")
                            
                        if total_precip_per_year > 1500:
                            st.error("🌧️ Heavy Rainfall! Ensure a sloped roof, deep drainage, and waterproofing.")
                        elif total_precip_per_year < 200:
                            st.warning("🏜️ Arid/Dry Climate. Rainwater harvesting is highly recommended.")
                        else:
                            st.success("🌦️ Moderate Rainfall. Standard roof slope is sufficient.")
                            
                        if max_wind > 80:
                            st.error("🌪️ High Wind Zone! Shelter must have a reinforced structural frame and aerodynamic roof design.")
                        elif avg_wind > 20:
                            st.warning("💨 Windy Area. Consider windbreaks and secure roofing materials.")
                            
                        if avg_hum > 75:
                            st.warning("💧 High Humidity! Use moisture-resistant materials and anti-fungal paints to prevent mold.")
                            
                        if avg_soil_m > 0.3:
                            st.warning("🌱 Wet/Saturated Soil. A raised foundation or strong damp-proofing course is essential.")
                            
                        if avg_solar > 20:
                            st.success("☀️ High Solar Radiance! Highly recommended to install solar panels. Also requires good shade structures/overhangs.")
                        elif avg_solar < 10:
                            st.info("☁️ Low Solar Radiance. Maximize natural light with larger windows and skylights.")
                        
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: 3D Design & Thermodynamics ---
with tab2:
    rooms_data = []
    if "weather_data" not in st.session_state:
        st.warning("Please analyze weather data in Tab 1 first.")
    else:
        st.header("Shelter Design & Energy Simulator")
        
        col_design, col_viz = st.columns([1, 2])
        
        with col_viz:
            st.subheader("3D Architectural Model")
            c_v1, c_v2, c_v3 = st.columns(3)
            show_solid = c_v1.toggle("Solid Surfaces", value=True)
            show_scale = c_v2.toggle("Human Scale", value=True)
            show_ground = c_v3.toggle("Ground Plane", value=True)
            
            c_v4, c_v5, _ = st.columns([1, 1, 1])
            show_wind = c_v4.toggle("💨 Show Wind Flow", value=True)
            show_heat = c_v5.toggle("🔥 Show Heat Flow", value=True)
        
        with col_design:
            st.subheader("Structure Shape")
            build_mode = st.radio("Building Type", ["Single Shape", "Compound Structure (Base + Roof)", "Multi-Room (Modular)"])
            
            if build_mode != "Multi-Room (Modular)":
                st.subheader("Target Environment")
                optimal_temp = st.slider("Target Indoor Temp (°C)", 10.0, 30.0, 21.0)
            else:
                optimal_temp = 21.0  # Will be dynamically calculated as volume-weighted average
            
            area = 0
            roof_area = 0
            volume = 0
            floor_area = 0
            
            fig = go.Figure()
            
            # --- 3D Drawing Helpers ---
            wd = st.session_state.weather_data
            def add_solid(fig, x, y, z, color='#3498db', opacity=0.4, force=False, is_ground=False, name=None, hovertext=None):
                if show_solid or force:
                    if show_heat and not is_ground:
                        # Heat-map visualization: Temperature gradient based on height and weather
                        is_hot = wd["avg_temp"] > optimal_temp
                        cscale = 'Inferno' if is_hot else 'YlGnBu_r'
                        
                        # In summer, roof (high z) is extremely hot due to solar radiance.
                        # In winter, roof is extremely cold due to deep space radiative cooling.
                        # We map the Z coordinates to a normalized intensity array.
                        z_min, z_max = min(z), max(z)
                        if z_max == z_min: z_max = z_min + 1
                        
                        if is_hot:
                            intensity = [(zi - z_min) / (z_max - z_min) for zi in z] # Higher is hotter
                        else:
                            intensity = [1.0 - ((zi - z_min) / (z_max - z_min)) for zi in z] # Higher is colder (lower intensity in YlGnBu_r)
                            
                        fig.add_trace(go.Mesh3d(
                            x=x, y=y, z=z, 
                            intensity=intensity, colorscale=cscale, 
                            opacity=0.85, alphahull=0, name=name, hoverinfo='text' if hovertext else None, hovertext=hovertext
                        ))
                    else:
                        fig.add_trace(go.Mesh3d(x=x, y=y, z=z, color=color, opacity=opacity, alphahull=0, name=name, hoverinfo='text' if hovertext else None, hovertext=hovertext))
                    
            def apply_transform(x_list, y_list, x_offset, y_offset, rot_deg):
                rad = np.radians(rot_deg)
                c, s = np.cos(rad), np.sin(rad)
                x_new, y_new = [], []
                for x, y in zip(x_list, y_list):
                    rx = x * c - y * s
                    ry = x * s + y * c
                    x_new.append(rx + x_offset)
                    y_new.append(ry + y_offset)
                return x_new, y_new

            def draw_box(fig, l, w, h, z_offset=0, x_offset=0, y_offset=0, rot_deg=0, name=None, hovertext=None):
                x = [0, l, l, 0, 0, 0, l, l, 0, 0, l, l, 0, 0, l, l]
                y = [0, 0, w, w, 0, 0, 0, w, w, 0, 0, 0, w, w, w, w]
                x, y = apply_transform(x, y, x_offset, y_offset, rot_deg)
                z = [z_offset, z_offset, z_offset, z_offset, z_offset, h+z_offset, h+z_offset, h+z_offset, h+z_offset, h+z_offset, h+z_offset, z_offset, z_offset, h+z_offset, h+z_offset, z_offset]
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='darkblue', width=4)))
                add_solid(fig, x, y, z, name=name, hovertext=hovertext)
            
            def draw_cylinder(fig, r, h, z_offset=0, x_offset=0, y_offset=0, rot_deg=0, name=None, hovertext=None):
                u = np.linspace(0, 2 * np.pi, 30)
                x_c = list(r * np.cos(u) + r)
                y_c = list(r * np.sin(u) + r)
                x_c, y_c = apply_transform(x_c, y_c, x_offset, y_offset, rot_deg)
                z_base = list(np.zeros_like(u) + z_offset)
                z_top = list(np.ones_like(u) * h + z_offset)
                fig.add_trace(go.Scatter3d(x=x_c, y=y_c, z=z_base, mode='lines', line=dict(color='darkblue', width=4)))
                fig.add_trace(go.Scatter3d(x=x_c, y=y_c, z=z_top, mode='lines', line=dict(color='darkblue', width=4)))
                for i in range(0, len(u), 5):
                    fig.add_trace(go.Scatter3d(x=[x_c[i], x_c[i]], y=[y_c[i], y_c[i]], z=[z_offset, h+z_offset], mode='lines', line=dict(color='darkblue', width=2)))
                x_solid = x_c + x_c
                y_solid = y_c + y_c
                z_solid = z_base + z_top
                add_solid(fig, x_solid, y_solid, z_solid, name=name, hovertext=hovertext)
            
            def draw_dome(fig, r, z_offset=0, x_offset=0, y_offset=0, rot_deg=0, name=None, hovertext=None):
                u = np.linspace(0, 2 * np.pi, 30)
                v = np.linspace(0, np.pi / 2, 15)
                x = list(r * np.outer(np.cos(u), np.sin(v)).flatten() + r)
                y = list(r * np.outer(np.sin(u), np.sin(v)).flatten() + r)
                x, y = apply_transform(x, y, x_offset, y_offset, rot_deg)
                z = list(r * np.outer(np.ones(np.size(u)), np.cos(v)).flatten() + z_offset)
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='darkblue', width=1), opacity=0.3))
                add_solid(fig, x, y, z, name=name, hovertext=hovertext)
                
            def draw_a_frame(fig, l, w, h, z_offset=0, x_offset=0, y_offset=0, rot_deg=0, name=None, hovertext=None):
                x = [0, l, l, 0, 0, 0, l, l, 0, l]
                y = [0, 0, w, w, 0, w/2, w/2, 0, w, w/2]
                x, y = apply_transform(x, y, x_offset, y_offset, rot_deg)
                z = [z_offset, z_offset, z_offset, z_offset, z_offset, h+z_offset, h+z_offset, z_offset, z_offset, h+z_offset]
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='darkblue', width=4)))
                add_solid(fig, x, y, z, name=name, hovertext=hovertext)
                
            def draw_pyramid_roof(fig, l, w, h, z_offset=0, x_offset=0, y_offset=0, rot_deg=0, name=None, hovertext=None):
                x = [0, l, l, 0, 0, l/2, l, l/2, 0, l/2, l]
                y = [0, 0, w, w, 0, w/2, 0, w/2, w, w/2, w]
                x, y = apply_transform(x, y, x_offset, y_offset, rot_deg)
                z = [z_offset, z_offset, z_offset, z_offset, z_offset, h+z_offset, z_offset, h+z_offset, z_offset, h+z_offset, z_offset]
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='darkblue', width=4)))
                add_solid(fig, x, y, z, name=name, hovertext=hovertext)

            # --- SHAPE LOGIC ---
            if build_mode == "Single Shape":
                shape = st.selectbox("Base Shape", ["Box", "Dome", "Triangular (A-Frame)", "Cylinder"])
                
                if shape == "Box":
                    length = st.slider("Length (m)", 2.0, 20.0, 5.0)
                    width = st.slider("Width (m)", 2.0, 20.0, 5.0)
                    height = st.slider("Height (m)", 2.0, 10.0, 3.0)
                    wall_area = 2 * (length*height + width*height)
                    roof_surface_area = length * width
                    roof_area = length * width # Projected for solar
                    floor_area = length * width
                    volume = length * width * height
                    draw_box(fig, length, width, height)
                    
                elif shape == "Dome":
                    radius = st.slider("Radius (m)", 2.0, 15.0, 5.0)
                    height = radius
                    wall_area = 0 # It's all roof
                    roof_surface_area = 2 * np.pi * radius**2
                    roof_area = np.pi * radius**2
                    floor_area = np.pi * radius**2
                    volume = (2/3) * np.pi * radius**3
                    draw_dome(fig, radius)
                    
                elif shape == "Triangular (A-Frame)":
                    length = st.slider("Length (m)", 2.0, 20.0, 5.0)
                    width = st.slider("Base Width (m)", 2.0, 20.0, 5.0)
                    height = st.slider("Ridge Height (m)", 2.0, 10.0, 4.0)
                    slant = np.sqrt((width/2)**2 + height**2)
                    wall_area = width * height # Two triangular end caps (2 * 0.5 * W * H)
                    roof_surface_area = 2 * length * slant
                    roof_area = length * width
                    floor_area = length * width
                    volume = 0.5 * width * height * length
                    draw_a_frame(fig, length, width, height)
                    
                elif shape == "Cylinder":
                    radius = st.slider("Radius (m)", 2.0, 15.0, 5.0)
                    height = st.slider("Height (m)", 2.0, 15.0, 3.0)
                    wall_area = 2 * np.pi * radius * height
                    roof_surface_area = np.pi * radius**2
                    roof_area = np.pi * radius**2
                    floor_area = np.pi * radius**2
                    volume = np.pi * radius**2 * height
                    draw_cylinder(fig, radius, height)
                    
            elif build_mode == "Compound Structure (Base + Roof)":
                base_shape = st.selectbox("Base Shape", ["Box", "Cylinder"])
                if base_shape == "Box":
                    b_length = st.slider("Base Length (m)", 2.0, 20.0, 5.0)
                    b_width = st.slider("Base Width (m)", 2.0, 20.0, 5.0)
                    b_height = st.slider("Base Height (m)", 2.0, 10.0, 3.0)
                    floor_area = b_length * b_width
                    wall_area = 2 * (b_length * b_height + b_width * b_height)
                    volume += b_length * b_width * b_height
                    roof_area = b_length * b_width
                    draw_box(fig, b_length, b_width, b_height)
                else:
                    b_radius = st.slider("Base Radius (m)", 2.0, 15.0, 5.0)
                    b_height = st.slider("Base Height (m)", 2.0, 10.0, 3.0)
                    floor_area = np.pi * b_radius**2
                    wall_area = 2 * np.pi * b_radius * b_height
                    volume += np.pi * b_radius**2 * b_height
                    roof_area = np.pi * b_radius**2
                    draw_cylinder(fig, b_radius, b_height)
                    
                roof_shape = st.selectbox("Roof Shape", ["Flat", "Pitched (Pyramid)", "Dome"])
                r_height = st.slider("Roof Height (m)", 0.0, 10.0, 2.0)
                
                if roof_shape == "Flat":
                    roof_surface_area = roof_area
                elif roof_shape == "Pitched (Pyramid)":
                    if base_shape == "Box":
                        slant_w = np.sqrt((b_width/2)**2 + r_height**2)
                        slant_l = np.sqrt((b_length/2)**2 + r_height**2)
                        roof_surface_area = (b_length * slant_w) + (b_width * slant_l)
                        volume += (1/3) * (b_length * b_width) * r_height
                        draw_pyramid_roof(fig, b_length, b_width, r_height, z_offset=b_height)
                    else:
                        slant = np.sqrt(b_radius**2 + r_height**2)
                        roof_surface_area = np.pi * b_radius * slant
                        volume += (1/3) * np.pi * b_radius**2 * r_height
                        draw_dome(fig, b_radius, z_offset=b_height)
                elif roof_shape == "Dome":
                    if base_shape == "Box":
                        r_eff = min(b_length, b_width) / 2
                        roof_surface_area = 2 * np.pi * r_eff**2
                        volume += (2/3) * np.pi * r_eff**3
                    else:
                        roof_surface_area = 2 * np.pi * b_radius**2
                        volume += (2/3) * np.pi * b_radius**3
                        draw_dome(fig, b_radius, z_offset=b_height)
                        
            elif build_mode == "Multi-Room (Modular)":
                num_rooms = st.slider("Number of Rooms", 1, 10, 2)
                
                # Safe initialization for hovertext
                wall_material = st.session_state.get('wall_mat_input', 'Brick (Solid)')
                roof_material = st.session_state.get('roof_mat_input', 'Wood (Softwood)')

                
                if st.button("✨ AI: Auto-Arrange Rooms for Optimal Temp"):
                    outdoor_temp = wd["avg_temp"]
                    is_hot = outdoor_temp > 21.0
                    
                    if is_hot:
                        for i in range(num_rooms):
                            st.session_state[f"x_{i}"] = float(i * 6.0)
                            st.session_state[f"y_{i}"] = 0.0
                            st.session_state[f"rot_{i}"] = 0
                    else:
                        import math
                        cols = math.ceil(math.sqrt(num_rooms))
                        for i in range(num_rooms):
                            st.session_state[f"x_{i}"] = float((i % cols) * 5.0)
                            st.session_state[f"y_{i}"] = float((i // cols) * 5.0)
                            st.session_state[f"rot_{i}"] = 0
                    
                    st.rerun()
                wall_area = 0
                roof_surface_area = 0
                roof_area = 0
                floor_area = 0
                volume = 0
                sum_temp_vol = 0
                

                
                for i in range(num_rooms):
                    st.markdown(f"**Room {i+1}**")
                    r_shape = st.selectbox(f"Shape - Room {i+1}", ["Box", "Dome", "Triangular (A-Frame)", "Cylinder"], key=f"shape_{i}")
                    r_temp = st.slider(f"Target Indoor Temp - Room {i+1} (°C)", 10.0, 30.0, 21.0, key=f"target_temp_{i}")
                    
                    c_x, c_y, c_rot = st.columns([2, 2, 1])
                    r_x = c_x.number_input("X Position (m)", -50.0, 50.0, float(i * 5.0), key=f"x_{i}")
                    r_y = c_y.number_input("Y Position (m)", -50.0, 50.0, 0.0, key=f"y_{i}")
                    r_rot = c_rot.selectbox("Rotate (°)", [0, 90, 180, 270], key=f"rot_{i}")
                    
                    r_l, r_w, r_h = 0, 0, 0
                    r_radius = 0.0
                    room_wall_area = 0
                    r_surface = 0
                    r_roof_area = 0
                    r_volume = 0
                    
                    if r_shape == "Box":
                        c_l, c_w, c_h = st.columns(3)
                        r_l = c_l.number_input("Length (m)", 2.0, 15.0, 5.0, key=f"l_{i}")
                        r_w = c_w.number_input("Width (m)", 2.0, 15.0, 5.0, key=f"w_{i}")
                        r_h = c_h.number_input("Height (m)", 2.0, 5.0, 3.0, key=f"h_{i}")
                        room_wall_area = 2 * (r_l * r_h + r_w * r_h)
                        r_surface = r_l * r_w
                        r_roof_area = r_l * r_w
                        r_volume = r_l * r_w * r_h
                        draw_box(fig, r_l, r_w, r_h, x_offset=r_x, y_offset=r_y, rot_deg=r_rot, name=f'Room {i+1}', hovertext=f'<b>Room {i+1}</b><br>Wall: {wall_material}<br>Roof: {roof_material}')
                        
                    elif r_shape == "Dome":
                        r_radius = st.number_input("Radius (m)", 2.0, 15.0, 5.0, key=f"rad_{i}")
                        r_l = r_radius * 2
                        r_w = r_radius * 2
                        r_h = r_radius
                        room_wall_area = 0
                        r_surface = 2 * np.pi * r_radius**2
                        r_roof_area = np.pi * r_radius**2
                        r_volume = (2/3) * np.pi * r_radius**3
                        draw_dome(fig, r_radius, x_offset=r_x, y_offset=r_y, rot_deg=r_rot, name=f'Room {i+1}', hovertext=f'<b>Room {i+1}</b><br>Wall: {wall_material}<br>Roof: {roof_material}')
                        
                    elif r_shape == "Triangular (A-Frame)":
                        c_l, c_w, c_h = st.columns(3)
                        r_l = c_l.number_input("Length (m)", 2.0, 20.0, 5.0, key=f"l_{i}")
                        r_w = c_w.number_input("Base Width (m)", 2.0, 20.0, 5.0, key=f"w_{i}")
                        r_h = c_h.number_input("Ridge Height (m)", 2.0, 10.0, 4.0, key=f"h_{i}")
                        slant = np.sqrt((r_w/2)**2 + r_h**2)
                        room_wall_area = r_w * r_h
                        r_surface = 2 * r_l * slant
                        r_roof_area = r_l * r_w
                        r_volume = 0.5 * r_w * r_h * r_l
                        draw_a_frame(fig, r_l, r_w, r_h, x_offset=r_x, y_offset=r_y, rot_deg=r_rot, name=f'Room {i+1}', hovertext=f'<b>Room {i+1}</b><br>Wall: {wall_material}<br>Roof: {roof_material}')
                        
                    elif r_shape == "Cylinder":
                        c_r, c_h = st.columns(2)
                        r_radius = c_r.number_input("Radius (m)", 2.0, 15.0, 5.0, key=f"rad_{i}")
                        r_h = c_h.number_input("Height (m)", 2.0, 15.0, 3.0, key=f"h_{i}")
                        r_l = r_radius * 2
                        r_w = r_radius * 2
                        room_wall_area = 2 * np.pi * r_radius * r_h
                        r_surface = np.pi * r_radius**2
                        r_roof_area = np.pi * r_radius**2
                        r_volume = np.pi * r_radius**2 * r_h
                        draw_cylinder(fig, r_radius, r_h, x_offset=r_x, y_offset=r_y, rot_deg=r_rot, name=f'Room {i+1}', hovertext=f'<b>Room {i+1}</b><br>Wall: {wall_material}<br>Roof: {roof_material}')
                    
                    # Bounding box collision for exact shared wall calculation
                    for j in range(i):
                        p = rooms_data[j]
                        x_overlap = max(0, min(r_x + r_l, p['x'] + p['l']) - max(r_x, p['x']))
                        y_overlap = max(0, min(r_y + r_w, p['y'] + p['w']) - max(r_y, p['y']))
                        
                        shared_area = 0
                        if x_overlap > 0 and y_overlap == 0:
                            shared_area = x_overlap * min(r_h, p['h'])
                        elif y_overlap > 0 and x_overlap == 0:
                            shared_area = y_overlap * min(r_h, p['h'])
                        elif x_overlap > 0 and y_overlap > 0:
                            shared_area = (x_overlap + y_overlap) * min(r_h, p['h'])
                            
                        if shared_area > 0:
                            if r_shape in ["Dome", "Cylinder"] or p['shape'] in ["Dome", "Cylinder"]:
                                shared_area = min(shared_area * 0.2, 4.0)
                            wall_area -= shared_area * 2
                            
                    rooms_data.append({'x': r_x, 'y': r_y, 'l': r_l, 'w': r_w, 'h': r_h, 'shape': r_shape, 'temp': r_temp, 'wall': room_wall_area, 'roof': r_surface, 'roof_proj': r_roof_area, 'vol': r_volume, 'rot': r_rot, 'rad': r_radius, 'wall_mat': wall_material, 'roof_mat': roof_material})
                        
                    wall_area += room_wall_area
                    roof_surface_area += r_surface
                    roof_area += r_roof_area
                    floor_area += r_l * r_w
                    volume += r_volume
                    sum_temp_vol += (r_volume * r_temp)

                if volume > 0:
                    optimal_temp = sum_temp_vol / volume
                else:
                    optimal_temp = 21.0

            # --- DOORS & WINDOWS ---
            st.subheader("Doors & Windows")
            
            c1, c2 = st.columns(2)
            with c1:
                num_doors = st.number_input("Number of Doors", 0, 100, 1)
                door_shape = st.selectbox("Door Shape", ["Rectangular", "Triangular", "Circular"])
                d_w = st.slider("Door Width (m)", 0.5, 3.0, 1.0)
                d_h = st.slider("Door Height (m)", 1.0, 3.0, 2.0)
                if door_shape == "Rectangular":
                    door_area_each = d_w * d_h
                elif door_shape == "Triangular":
                    door_area_each = 0.5 * d_w * d_h
                elif door_shape == "Circular":
                    door_area_each = np.pi * (d_w/2) * (d_h/2)
            
            with c2:
                num_windows = st.number_input("Number of Windows", 0, 100, 2)
                win_shape = st.selectbox("Window Shape", ["Rectangular", "Triangular", "Circular"])
                w_w = st.slider("Window Width (m)", 0.5, 3.0, 1.0)
                w_h = st.slider("Window Height (m)", 0.5, 3.0, 1.0)
                if win_shape == "Rectangular":
                    window_area_each = w_w * w_h
                elif win_shape == "Triangular":
                    window_area_each = 0.5 * w_w * w_h
                elif win_shape == "Circular":
                    window_area_each = np.pi * (w_w/2) * (w_h/2)
            
            total_door_area = num_doors * door_area_each
            total_window_area = num_windows * window_area_each
            total_openings_area = total_door_area + total_window_area
            
            solid_wall_area = wall_area - total_openings_area
            if solid_wall_area < 0:
                st.error("Error: Doors and windows exceed total wall area! Increase building size.")
                solid_wall_area = 0

            st.subheader("Ökobaudat Materials & Envelope")
            wall_material = st.selectbox("Primary Wall Material", list(MATERIALS.keys()), index=list(MATERIALS.keys()).index("Brick (Solid)"))
            roof_material = st.selectbox("Primary Roof Material", list(MATERIALS.keys()), index=list(MATERIALS.keys()).index("Wood (Softwood)"))
            wall_thickness = st.slider("Wall Thickness (m)", 0.05, 0.5, 0.2, step=0.01, help="Heat Conduction Formula: Q = (k × A × ΔT) / thickness")
            roof_thickness = st.slider("Roof Thickness (m)", 0.05, 0.5, 0.2, step=0.01, help="Heat Conduction Formula: Q = (k × A × ΔT) / thickness")
            
            u_wall = MATERIALS[wall_material]["u_value"]
            u_roof = MATERIALS[roof_material]["u_value"]
            abs_roof = MATERIALS[roof_material]["absorptance"]
            
            mat_density_wall = MATERIALS[wall_material]["density"]
            mat_embodied_wall = MATERIALS[wall_material]["embodied_energy"]
            mat_gwp_wall = MATERIALS[wall_material]["gwp"]
            
            mat_density_roof = MATERIALS[roof_material]["density"]
            mat_embodied_roof = MATERIALS[roof_material]["embodied_energy"]
            mat_gwp_roof = MATERIALS[roof_material]["gwp"]
            
            u_door = 3.0 
            u_window = 2.8 
            
        with col_viz:
            if show_ground:
                # Add a solid earthy ground plane that extends beyond the structure
                gx = [-10, 30, 30, -10, -10, 30, 30, -10]
                gy = [-10, -10, 30, 30, -10, -10, 30, 30]
                gz = [-0.2, -0.2, -0.2, -0.2, 0, 0, 0, 0]
                add_solid(fig, gx, gy, gz, color='#d3c2b0', opacity=1.0, force=True, is_ground=True)
                
            if show_scale:
                # Add a 1.8m tall "Human" box for scale reference (standing near the front corner)
                hx = [-1.5, -1, -1, -1.5, -1.5, -1, -1, -1.5]
                hy = [-1.5, -1.5, -1, -1, -1.5, -1.5, -1, -1]
                hz = [0, 0, 0, 0, 1.8, 1.8, 1.8, 1.8]
                add_solid(fig, hx, hy, hz, color='#e67e22', opacity=1.0, force=True, is_ground=True)
            if num_doors > 0:
                # Solid brown door
                d_x = [0, d_w, d_w, 0, 0, d_w, d_w, 0]
                d_y = [-0.1, -0.1, -0.1, -0.1, 0, 0, 0, 0]
                d_z = [0, 0, d_h, d_h, 0, 0, d_h, d_h]
                fig.add_trace(go.Mesh3d(x=d_x, y=d_y, z=d_z, color='#8B4513', alphahull=0, name="Door"))
                fig.add_trace(go.Scatter3d(x=[0, d_w, d_w, 0, 0], y=[-0.1, -0.1, -0.1, -0.1, -0.1], z=[0, 0, d_h, d_h, 0], mode='lines', line=dict(color='black', width=3), name="Door Frame"))
                
            if num_windows > 0:
                # Translucent glass window
                w_x = [0, w_w, w_w, 0, 0, w_w, w_w, 0]
                w_y = [-0.1, -0.1, -0.1, -0.1, 0, 0, 0, 0]
                w_z = [d_h+0.5, d_h+0.5, d_h+0.5+w_h, d_h+0.5+w_h, d_h+0.5, d_h+0.5, d_h+0.5+w_h, d_h+0.5+w_h]
                fig.add_trace(go.Mesh3d(x=w_x, y=w_y, z=w_z, color='#87CEEB', opacity=0.6, alphahull=0, name="Window"))
                fig.add_trace(go.Scatter3d(x=[0, w_w, w_w, 0, 0], y=[-0.1, -0.1, -0.1, -0.1, -0.1], z=[d_h+0.5, d_h+0.5, d_h+0.5+w_h, d_h+0.5+w_h, d_h+0.5], mode='lines', line=dict(color='black', width=3), name="Window Frame"))
                
            if show_wind:
                # --- Wind Flow (Cool Blue Vectors moving across X-axis) ---
                wx, wy, wz, wu, wv, ww = [], [], [], [], [], []
                for xp in range(-5, 20, 5):
                    for yp in range(-5, 15, 5):
                        for zp in [1.5, 3.0]:  # Flowing at human height and window height
                            wx.append(xp)
                            wy.append(yp)
                            wz.append(zp)
                            wu.append(3) # Wind velocity along +X
                            wv.append(0)
                            ww.append(0)
                
                fig.add_trace(go.Cone(
                    x=wx, y=wy, z=wz, u=wu, v=wv, w=ww,
                    colorscale='Blues', sizemode='absolute', sizeref=1.5, showscale=False, opacity=0.6, name="Wind"
                ))
                
            if show_heat:
                # --- Heat Flow (Hot Red Vectors rising from Roof) ---
                hx, hy, hz, hu, hv, hw = [], [], [], [], [], []
                for xp in range(0, 15, 4):
                    for yp in range(0, 15, 4):
                        for zp in [4.5, 6.0, 7.5]: # Rising up from roof level
                            hx.append(xp)
                            hy.append(yp)
                            hz.append(zp)
                            hu.append(0)
                            hv.append(0)
                            hw.append(2) # Heat rising along +Z
                            
                fig.add_trace(go.Cone(
                    x=hx, y=hy, z=hz, u=hu, v=hv, w=hw,
                    colorscale='YlOrRd', sizemode='absolute', sizeref=1.5, showscale=False, opacity=0.8, name="Heat"
                ))
            # Render the parametric 3D Plotly architecture (supports multi-room, roofs, windows)
            fig.update_layout(scene=dict(aspectmode="data"), margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
            st.plotly_chart(fig, width='stretch')
            
            st.markdown("---")
            
            # Show the standalone WebGL wind simulator
            st.markdown("### 🌪️ Advanced WebGL Aerodynamic Simulator")
            st.caption("Drag to orbit · Scroll to zoom · Interact with the HUD to test base shapes and wind speeds.")
            with open("windform.html", "r", encoding="utf-8") as f:
                windform_html = f.read()
            components.html(windform_html, height=700)

            # --- AI ARCHITECTURAL SUGGESTIONS ---
            st.markdown("### 🤖 Architectural Recommendations")
            st.info(f"**Total Internal Volume:** {volume:.1f} m³ | **Floor Area:** {floor_area:.1f} m²")
            
            capacity = max(1, int(volume / 30))
            st.write(f"- **Capacity:** Optimal for ~{capacity} people.")
            
            opt_win_area = floor_area * 0.15
            if total_window_area < (opt_win_area * 0.5):
                st.warning(f"- **Windows:** You have {total_window_area:.1f} m² of windows. It is highly recommended to increase this to ~{opt_win_area:.1f} m² for natural lighting and healthy cross-ventilation.")
            elif total_window_area > (opt_win_area * 2):
                st.warning(f"- **Windows:** You have {total_window_area:.1f} m² of windows, which is huge! This will cause massive heat loss/gain. Consider reducing to ~{opt_win_area:.1f} m².")
            else:
                st.success(f"- **Windows:** Your window area ({total_window_area:.1f} m²) is perfectly balanced for this volume (ideal is ~{opt_win_area:.1f} m²).")

        st.markdown("---")
        st.header(f"Thermodynamic & Environmental Analysis (Target: {optimal_temp}°C)")
        
        # Calculate Material Volume & Environmental Impact
        wall_volume = solid_wall_area * wall_thickness
        roof_volume = roof_surface_area * wall_thickness
        
        mass_wall = wall_volume * mat_density_wall
        mass_roof = roof_volume * mat_density_roof
        total_mass = mass_wall + mass_roof
        
        total_embodied_energy = (mass_wall * mat_embodied_wall) + (mass_roof * mat_embodied_roof)
        total_gwp = (mass_wall * mat_gwp_wall) + (mass_roof * mat_gwp_roof)
        
        st.markdown(f"""
        **Total Material Mass:** {total_mass:,.0f} kg ({mass_wall:,.0f} kg Walls, {mass_roof:,.0f} kg Roof)
        """)
        
        env1, env2 = st.columns(2)
        env1.metric("🌍 Total Embodied Energy (Production)", f"{total_embodied_energy:,.0f} MJ")
        
        if total_gwp < 0:
            env2.metric("🌱 Total Global Warming Potential (GWP)", f"{total_gwp:,.0f} kg CO2-eq", "Carbon Sink!", delta_color="normal")
        else:
            env2.metric("🏭 Total Global Warming Potential (GWP)", f"{total_gwp:,.0f} kg CO2-eq")
            
        # --- PASSIVE INDOOR TEMPERATURE MODEL ---
        st.header("🌡️ Passive Indoor Temperature (No AC/Heating)")
        st.write("Calculates natural indoor temperatures using strict exponential thermal mass decay (τ), wind-driven convection, and deep space radiative cooling.")
        
        st.markdown("---")
        st.header("Passive Indoor Temperature Prediction")
        
        wd = st.session_state.weather_data
        u_window = 2.8
        u_door = 2.0
        
        # 1. Base Assumptions
        air_heat_capacity = volume * 1.2 * 1000 # J/K
        k_wall = u_wall
        k_roof = u_roof
        
        wind_m_s = wd.get("avg_wind", 10.0) * (1000/3600)
        h_out = 5.7 + 3.8 * wind_m_s  
        h_in = 8.0  
        
        # Calculate full U-value including boundary convective layers (R_total = R_in + R_cond + R_out)
        # Note: The pure conduction part (R_cond = thickness/k) is shown in the UI slider.
        true_u_wall = 1 / ((1/h_in) + (wall_thickness / k_wall) + (1/h_out)) if k_wall > 0 else 0
        true_u_roof = 1 / ((1/h_in) + (roof_thickness / k_roof) + (1/h_out)) if k_roof > 0 else 0
        
        U_A_conductive = (true_u_wall * solid_wall_area) + (true_u_roof * roof_surface_area) + (u_window * total_window_area) + (u_door * total_door_area)
        
        infiltration_m3_s = (volume * 0.5) / 3600
        effective_open_area = total_window_area * 0.1
        airflow_m3_s = (effective_open_area * wind_m_s * 0.5) + infiltration_m3_s
        U_A_ventilation = airflow_m3_s * 1200
        
        U_A = U_A_conductive + U_A_ventilation
        if U_A == 0: U_A = 0.1 
        
        num_people = max(1, int(volume / 40))
        Q_internal = num_people * 80  
        
        solar_radiance_w_m2 = wd["avg_solar_mj"] * 11.57
        Q_solar_roof = solar_radiance_w_m2 * roof_area * abs_roof
        
        # Generalized Window Solar Gain (assuming ~50% of window area effectively captures sun at an SHGC of 0.6)
        SHGC = 0.6
        Q_solar_windows = solar_radiance_w_m2 * (total_window_area * 0.5) * SHGC
        Q_solar_avg = Q_solar_roof + Q_solar_windows
        Q_solar_peak = Q_solar_avg * 2.5
        total_internal_heat_w = Q_internal
        
        # 4. Thermal Mass (τ) Calculation
        cp_dict = {
            "Concrete (Standard)": 840, "Concrete (Aerated)": 1000, "Brick (Solid)": 840,
            "Brick (Hollow)": 840, "Wood (Softwood)": 1600, "Wood (Hardwood)": 1600,
            "Steel (Galvanized)": 450, "Aluminum (Sheet)": 900, "Adobe / Mudbrick": 1000,
            "Rammed Earth": 1000, "Straw Bale": 2000, "SIPs (Insulated Panels)": 1400,
            "Stone (Granite/Marble)": 800, "Bamboo": 1600
        }
        cp_wall = cp_dict.get(wall_material, 1000)
        
        tau_seconds = (mat_density_wall * cp_wall * (wall_thickness**2)) / k_wall if k_wall > 0 else 3600
        tau_hours = tau_seconds / 3600.0
        
        # 5. Radiative Heat Loss at Night (Deep Space Cooling)
        sigma = 5.67e-8
        epsilon = 0.9
        T_ambient_night_K = wd["ext_min"] + 273.15
        T_sky_K = T_ambient_night_K - 15.0 # Clear night sky is ~15K colder than ambient air
        Q_rad_total_W = epsilon * sigma * roof_surface_area * (T_ambient_night_K**4 - T_sky_K**4)
        
        # Baseline temperature drops below ambient due to radiative loss to space
        T_night_baseline = wd["ext_min"] - (Q_rad_total_W / U_A)
        
        # 6. Temperature Predictions
        t_in_avg = wd["avg_temp"] + (Q_solar_avg + Q_internal) / U_A
        t_in_max_undamped = wd["ext_max"] + (Q_solar_peak + Q_internal) / U_A
        delta_t_day = t_in_max_undamped - wd["ext_max"]
        
        night_hours = 8.0
        decay_factor = np.exp(-night_hours / max(tau_hours, 0.1))
        
        t_in_min_undamped = T_night_baseline + (Q_internal / U_A)
        t_in_min = t_in_min_undamped + (delta_t_day * decay_factor)
        
        daytime_dampening = 1.0 - np.exp(-12.0 / max(tau_hours, 0.1))
        t_in_max = t_in_avg + (t_in_max_undamped - t_in_avg) * daytime_dampening
        
        if build_mode == "Multi-Room (Modular)":
            st.subheader("Room-by-Room Baseline Performance (No AC)")
            st.write(f"Using selected materials: **{wall_material} walls** and **{roof_material} roof**")
            for idx, rm in enumerate(rooms_data):
                if rm.get('vol', 1) <= 0: rm['vol'] = 1.0  # prevent skip
                vol_ratio = rm['vol'] / max(volume, 1e-6)
                wall_ratio = rm['wall'] / max(wall_area, 1e-6)
                r_win = total_window_area * wall_ratio
                r_door = total_door_area * wall_ratio
                r_vent = U_A_ventilation * vol_ratio
                r_internal = Q_internal * vol_ratio
                r_UA_conductive = (true_u_wall * rm['wall']) + (true_u_roof * rm['roof']) + (u_window * r_win) + (u_door * r_door)
                r_UA = r_UA_conductive + r_vent
                if r_UA == 0: r_UA = 0.1
                r_Q_solar_roof = solar_radiance_w_m2 * rm['roof_proj'] * abs_roof
                r_Q_solar_win = solar_radiance_w_m2 * (r_win * 0.5) * SHGC
                r_Q_solar_avg = r_Q_solar_roof + r_Q_solar_win
                r_t_in_avg = wd["avg_temp"] + (r_Q_solar_avg + r_internal) / r_UA
                status = "✅ Spot on!" if abs(r_t_in_avg - rm['temp']) < 1.5 else ("🔥 Too Hot" if r_t_in_avg > rm['temp'] else "❄️ Too Cold")
                st.info(f"**Room {idx+1} (Target: {rm['temp']:.1f}°C)** | Current Materials naturally achieve **{r_t_in_avg:.1f}°C** -> {status}")
        else:
            t1, t2, t3 = st.columns(3)
            t1.metric("Avg Indoor Temp", f"{t_in_avg:.1f} °C", f"{t_in_avg - wd['avg_temp']:+.1f} °C vs Outdoor Avg", delta_color="off")
            t2.metric("Extreme Max Indoor", f"{t_in_max:.1f} °C", f"{t_in_max - wd['ext_max']:+.1f} °C vs Outdoor Max", delta_color="inverse")
            t3.metric("Extreme Min (Night) Temp", f"{t_in_min:.1f} °C", f"{t_in_min - wd['ext_min']:+.1f} °C vs Outdoor Min", delta_color="normal")
        
        st.caption(f"**Physics Diagnostics:** Thermal Time Constant (τ) = **{tau_hours:.1f} hours**. Natural Ventilation Heat Transfer = **{U_A_ventilation:,.0f} W/K** (driven by {wd.get('avg_wind', 0):.1f} km/h local wind).")

        st.markdown("---")
        st.header("🌬️ Smart Passive Ventilation Schedule")
        st.write(f"Based on your local weather and your target optimal temperature of **{optimal_temp}°C**, follow this schedule to naturally maintain shelter temperature without AC or Heating.")
        
        if wd["avg_temp"] < optimal_temp - 2:
            # Heating Season (Winter)
            st.info("**Current Season: HEATING REQUIRED (Winter-like)**")
            st.markdown("**Goal:** Trap internal heat and maximize passive solar gain.")
            st.markdown("""
| Time of Day | Windows & Doors | Strategy & Rationale |
| :--- | :--- | :--- |
| ☀️ **Daytime (09:00 - 15:00)** | 🛑 **CLOSED** | Allow sunlight in through the glass (greenhouse effect), but block cold air. If fresh air is needed, crack windows slightly for only 10-15 mins around 13:00 (peak outdoor temp). |
| 🌙 **Nighttime (15:00 - 09:00)** | 🛑 **CLOSED** | Keep everything tightly sealed against drafts. The thermal mass of your walls will release the heat trapped during the day into the shelter. |
            """)
        elif wd["avg_temp"] > optimal_temp + 2:
            # Cooling Season (Summer)
            st.error("**Current Season: COOLING REQUIRED (Summer-like)**")
            st.markdown("**Goal:** Block daytime heat and purge thermal mass at night (Night Flushing).")
            st.markdown("""
| Time of Day | Windows & Doors | Strategy & Rationale |
| :--- | :--- | :--- |
| ☀️ **Daytime (08:00 - 18:00)** | 🛑 **CLOSED** | Keep tightly closed and shaded. Outdoor air is hotter than your target temp; opening windows will heat up the shelter. Let the walls absorb internal heat. |
| 🌙 **Nighttime (18:00 - 08:00)** | 💨 **FULLY OPEN** | The outside air is cooler at night. This enables "night flushing," pulling cool air through the shelter to strip heat out of the walls and reset them for the next day. |
            """)
        else:
            # Mild Season
            st.success("**Current Season: MILD (Comfortable)**")
            st.markdown("**Goal:** Maintain fresh air flow.")
            st.markdown("""
| Time of Day | Windows & Doors | Strategy & Rationale |
| :--- | :--- | :--- |
| ☀️ **Daytime** | 💨 **OPEN** | Keep freely open for natural cross-ventilation and fresh air. |
| 🌙 **Nighttime** | 💨 **OPEN / PARTIAL** | Keep open or partially closed depending on personal comfort and security. |
            """)

        st.markdown("---")

        if build_mode == 'Multi-Room (Modular)':
            st.header('⚡ Active HVAC Energy Analysis (Room-by-Room)')
            total_heating = 0
            total_cooling = 0
            total_loss = 0
            total_solar = 0
            
            for idx, rm in enumerate(rooms_data):
                if rm.get('vol', 1) <= 0: rm['vol'] = 1.0  # prevent skip
                # Apportion
                vol_ratio = rm['vol'] / max(volume, 1e-6)
                wall_ratio = rm['wall'] / max(wall_area, 1e-6)
                r_win = total_window_area * wall_ratio
                r_door = total_door_area * wall_ratio
                r_vent = U_A_ventilation * vol_ratio
                
                # Room UA
                r_UA = (true_u_wall * rm['wall']) + (true_u_roof * rm['roof']) + (u_window * r_win) + (u_door * r_door) + r_vent
                
                # Heat loss & solar gain for room
                r_delta_t = abs(wd['avg_temp'] - rm['temp'])
                r_heat_loss_kwh = (r_UA * r_delta_t * 24 * 365) / 1000
                total_loss += r_heat_loss_kwh
                
                r_Q_solar_roof = solar_radiance_w_m2 * rm['roof_proj'] * abs_roof
                r_Q_solar_win = solar_radiance_w_m2 * (r_win * 0.5) * SHGC
                r_solar_gain_kwh = ((r_Q_solar_roof + r_Q_solar_win) * 24 * 365) / 1000
                total_solar += r_solar_gain_kwh
                
                if wd['avg_temp'] < rm['temp']:
                    r_net = max(0, r_heat_loss_kwh - r_solar_gain_kwh)
                    total_heating += r_net
                    r_mode = 'Heating'
                else:
                    r_net = r_heat_loss_kwh + r_solar_gain_kwh
                    total_cooling += r_net
                    r_mode = 'Cooling'
                    
                st.info(f'**Room {idx+1} (Target: {rm["temp"]:.1f}°C):** Requires **{r_net:,.0f} kWh/yr** of {r_mode}.')
                
            c1, c2, c3 = st.columns(3)
            c1.metric('Total Heat Loss/Transfer', f'{total_loss:,.0f} kWh/yr')
            c2.metric('Total Solar Gain', f'{total_solar:,.0f} kWh/yr')
            c3.metric('Total Net HVAC Load', f'{total_heating + total_cooling:,.0f} kWh/yr')
            best_orient = 'South-Facing (maximize winter sun)' if total_heating > total_cooling else 'North-Facing (minimize direct sun)'
            
        else:
            st.header(f"⚡ Active HVAC Energy Analysis (Target: {optimal_temp}°C)")
            delta_t = abs(wd["avg_temp"] - optimal_temp)
            heat_loss_w = U_A * delta_t
            heat_loss_kwh_yr = (heat_loss_w * 24 * 365) / 1000
            solar_gain_kwh_yr = (Q_solar_avg * 24 * 365) / 1000
            
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("Total Heat Loss/Transfer", f"{heat_loss_kwh_yr:,.0f} kWh/yr")
            col_res2.metric("Solar Heat Gain", f"{solar_gain_kwh_yr:,.0f} kWh/yr")
            
            if wd["avg_temp"] < optimal_temp:
                net_energy = max(0, heat_loss_kwh_yr - solar_gain_kwh_yr)
                col_res3.metric(f"Heating Req. (to reach {optimal_temp}°C)", f"{net_energy:,.0f} kWh/yr")
                best_orient = "South-Facing (maximize winter sun)"
            else:
                net_energy = heat_loss_kwh_yr + solar_gain_kwh_yr
                col_res3.metric(f"Cooling Req. (to reach {optimal_temp}°C)", f"{net_energy:,.0f} kWh/yr")
                best_orient = "North-Facing (minimize direct sun)"
                
        delta_t = abs(wd['avg_temp'] - optimal_temp)
        if build_mode == 'Multi-Room (Modular)':
            solar_gain_kwh_yr = total_solar
        st.subheader(f"Ökobaudat Wall Material Comparison (Keeping {roof_material} Roof)")
        comp_data = []
        
        for m_name, m_props in MATERIALS.items():
            m_k_wall = m_props["u_value"]
            m_true_u_wall = 1 / ((1/h_in) + (wall_thickness / m_k_wall) + (1/h_out)) if m_k_wall > 0 else 0
            m_U_A = (m_true_u_wall * solid_wall_area) + (true_u_roof * roof_surface_area) + (u_window * total_window_area) + (u_door * total_door_area) + U_A_ventilation
            
            hl_w = m_U_A * delta_t
            hl_kwh = (hl_w * 24 * 365) / 1000
            
            if wd["avg_temp"] < optimal_temp:
                n_en = max(0, hl_kwh - solar_gain_kwh_yr)
            else:
                n_en = hl_kwh + solar_gain_kwh_yr
                
            m_mass = wall_volume * m_props["density"]
            m_gwp = m_mass * m_props["gwp"] + (mass_roof * mat_gwp_roof)
            m_emb = m_mass * m_props["embodied_energy"] + (mass_roof * mat_embodied_roof)
            m_cost = (m_mass * m_props["cost_per_kg"] + (mass_roof * MATERIALS[roof_material]["cost_per_kg"])) * 83.0
                
            comp_data.append({
                "Wall Material": m_name, 
                "Net Energy (kWh/yr)": n_en,
                "GWP (kg CO2-eq)": m_gwp,
                "Total Cost (₹)": m_cost,
                "Embodied Energy (MJ)": m_emb,
                "Density (kg/m³)": m_props["density"]
            })
        
        df = pd.DataFrame(comp_data).sort_values("Net Energy (kWh/yr)")
        st.dataframe(df.style.format({
            "Net Energy (kWh/yr)": "{:,.0f}",
            "GWP (kg CO2-eq)": "{:,.0f}",
            "Total Cost (₹)": "₹{:,.2f}",
            "Embodied Energy (MJ)": "{:,.0f}"
        }), width='stretch')
        
        baseline = [c for c in comp_data if c["Wall Material"] == "Concrete (Standard)"][0]["Net Energy (kWh/yr)"]
        lowest_energy = df.iloc[0]["Net Energy (kWh/yr)"]
        best_mat = df.iloc[0]["Wall Material"]
        
        savings = 0
        if baseline > 0:
            savings = ((baseline - lowest_energy) / baseline) * 100
            
        st.success(f"🏆 **Most Energy Efficient Wall Material:** {best_mat}")
        
        df_env = df.sort_values("GWP (kg CO2-eq)")
        best_env_mat = df_env.iloc[0]["Wall Material"]
        st.success(f"🌱 **Most Eco-Friendly Wall Material:** {best_env_mat} (Lowest Global Emissions)")
        
        df_cost = df.sort_values("Total Cost (₹)")
        best_cost_mat = df_cost.iloc[0]["Wall Material"]
        best_cost_val = df_cost.iloc[0]["Total Cost (₹)"]
        
        user_cost = [c for c in comp_data if c["Wall Material"] == wall_material][0]["Total Cost (₹)"]
        cost_savings = user_cost - best_cost_val
        cost_savings_pct = (cost_savings / user_cost) * 100 if user_cost > 0 else 0
        
        if cost_savings > 0:
            st.info(f"💡 **Financial Tip:** By switching your wall material to **{best_cost_mat}**, you would save **₹{cost_savings:,.2f}** ({cost_savings_pct:.1f}%) in raw material costs compared to {wall_material}!")
        else:
            st.info(f"💵 **Cost Savings:** Your selected **{wall_material}** is already the most cost-efficient option for the walls!")
        
        st.info(f"🧭 **Best Orientation:** {best_orient}")
        st.info(f"⚡ **Energy Savings:** Using {best_mat} instead of Standard Concrete saves **{savings:.1f}%** in energy waste per year to maintain {optimal_temp}°C!")
        
        # --- AI OPTIMAL DESIGN FINDER ---
        st.divider()
        st.subheader("🏆 AI Optimal Design Recommendation")
        
        best_opt_energy = float('inf')
        best_opt_wall = ""
        best_opt_roof = ""
        
        avg_solar_w = wd["avg_solar_mj"] * (1000000 / 86400)
        
        for w_name, w_props in MATERIALS.items():
            for r_name, r_props in MATERIALS.items():
                opt_k_wall = w_props["u_value"]
                opt_k_roof = r_props["u_value"]
                
                opt_u_wall = 1 / ((1/h_in) + (wall_thickness / opt_k_wall) + (1/h_out)) if opt_k_wall > 0 else 0
                opt_u_roof = 1 / ((1/h_in) + (roof_thickness / opt_k_roof) + (1/h_out)) if opt_k_roof > 0 else 0
                
                opt_U_A = (opt_u_wall * solid_wall_area) + (opt_u_roof * roof_surface_area) + (u_window * total_window_area) + (u_door * total_door_area) + U_A_ventilation
                
                opt_abs_roof = r_props["absorptance"]
                opt_solar_w = (avg_solar_w * roof_surface_area * opt_abs_roof) + (avg_solar_w * total_window_area * 0.7)
                opt_solar_kwh_yr = (opt_solar_w * 24 * 365) / 1000
                
                opt_hl_w = opt_U_A * delta_t
                opt_hl_kwh_yr = (opt_hl_w * 24 * 365) / 1000
                
                if wd["avg_temp"] < optimal_temp:
                    opt_net = max(0, opt_hl_kwh_yr - opt_solar_kwh_yr)
                else:
                    opt_net = opt_hl_kwh_yr + opt_solar_kwh_yr
                    
                if opt_net < best_opt_energy:
                    best_opt_energy = opt_net
                    best_opt_wall = w_name
                    best_opt_roof = r_name

        st.success(f"""
        ### 🌟 The Ultimate Energy-Saving Shelter Configuration
        Based on evaluating all possible structural combinations for your local climate, here is the absolute optimal architectural design to minimize air conditioning and heating costs:

        *   **Optimal Wall Material:** {best_opt_wall}
        *   **Optimal Roof Material:** {best_opt_roof}
        *   **Ideal Orientation:** {best_orient}
        *   **Recommended Wall Thickness:** As thick as your budget allows! (Evaluated at {wall_thickness}m).
        
        By using this combination, your shelter will require **{best_opt_energy:,.0f} kWh/yr** of active HVAC energy to perfectly maintain {optimal_temp}°C year-round.
        """)
        

# ==========================================
# END OF TAB 2
# ==========================================
with tab3:
    if "weather_data" not in st.session_state:
        st.warning("Please analyze weather data in Tab 1 first.")
    else:
        # --- MOST OPTIMAL PASSIVE MATERIAL (ROOM-BY-ROOM) ---
        st.markdown("---")
        st.header("🏆 Most Optimal Passive Material Strategy")

        # Auto-fill rooms_data for ANY mode so the 3D Engine always works
        if not rooms_data:
            _ss = st.session_state
            rooms_data = [{
                'x': 0.0, 'y': 0.0,
                'l': float(_ss.get('b_length', 5.0)),
                'w': float(_ss.get('b_width', 5.0)),
                'h': float(_ss.get('b_height', 3.0)),
                'shape': 'Box',
                'rad': float(_ss.get('b_radius', 3.0)),
                'rot': 0,
                'wall_mat': _ss.get('wall_mat_input', 'Brick (Solid)'),
                'roof_mat': _ss.get('roof_mat_input', 'Wood (Softwood)'),
                'temp': float(_ss.get('target_temp', 21.0)),
                'vol': max(1.0, float(_ss.get('b_length', 5.0)) * float(_ss.get('b_width', 5.0)) * float(_ss.get('b_height', 3.0))),
                'wall': max(1.0, 2 * (float(_ss.get('b_length', 5.0)) + float(_ss.get('b_width', 5.0))) * float(_ss.get('b_height', 3.0))),
                'roof': max(1.0, float(_ss.get('b_length', 5.0)) * float(_ss.get('b_width', 5.0))),
                'roof_proj': max(1.0, float(_ss.get('b_length', 5.0)) * float(_ss.get('b_width', 5.0))),
            }]

        
        def find_best_passive_materials(
            target_t, w_area, r_surface, r_proj, vol_r,
            wall_thickness, roof_thickness,
            h_in, h_out,
            wall_area, volume,
            total_window_area, total_door_area,
            U_A_ventilation, Q_internal,
            u_window, u_door,
            wd, MATERIALS
        ):
            best_wall, best_roof, best_score = "", "", float('inf')
            best_t_avg = 0

            vol_ratio = vol_r / max(volume, 1e-6)
            wall_ratio = w_area / max(wall_area, 1e-6)
            r_win = total_window_area * wall_ratio
            r_door = total_door_area * wall_ratio
            r_vent = U_A_ventilation * vol_ratio
            r_internal = Q_internal * vol_ratio

            for wn, wp in MATERIALS.items():
                kw = wp["u_value"]
                if kw <= 0: continue

                for rn, rp in MATERIALS.items():
                    kr = rp["u_value"]
                    if kr <= 0: continue

                    uw = 1 / ((1 / h_in) + (wall_thickness / kw) + (1 / h_out))
                    ur = 1 / ((1 / h_in) + (roof_thickness / kr) + (1 / h_out))

                    UA = (uw * w_area) + (ur * r_surface) + (u_window * r_win) + (u_door * r_door) + r_vent
                    if UA <= 0: UA = 0.1

                    avg_solar_w = wd.get("avg_solar_mj", 15) * (1_000_000 / 86400)
                    sol = (avg_solar_w * r_proj * rp["absorptance"]) + (avg_solar_w * r_win * 0.5 * 0.6)

                    t_avg = wd["avg_temp"] + (sol + r_internal) / UA

                    # Minimize active HVAC required to maintain target_t
                    if wd["avg_temp"] > target_t:
                        score = UA * (wd["avg_temp"] - target_t) + sol + r_internal
                    else:
                        score = max(0, UA * (target_t - wd["avg_temp"]) - sol - r_internal)
                    if score < best_score:
                        best_score = score
                        best_wall = wn
                        best_roof = rn
                        best_t_avg = t_avg

            return best_wall, best_roof, best_t_avg

        if True:
            st.subheader("Room-by-Room Material Recommendations")
            for idx, rm in enumerate(rooms_data):
                if rm['vol'] > 0:
                    bw, br, bt = find_best_passive_materials(
                        rm["temp"], rm["wall"], rm["roof"], rm["roof_proj"], rm["vol"],
                        wall_thickness, roof_thickness,
                        h_in, h_out,
                        wall_area, volume,
                        total_window_area, total_door_area,
                        U_A_ventilation, Q_internal,
                        u_window, u_door,
                        wd, MATERIALS
                    )
                    st.success(f"**Room {idx+1} (Target: {rm['temp']:.1f}°C):** Use **{bw}** for walls and **{br}** for roof.")
                    st.caption(f"↳ This combination naturally balances heat to achieve **{bt:.1f}°C**.")
            
            import json
            import streamlit.components.v1 as components
            
            three_data = []
            for idx, rm in enumerate(rooms_data):
                if rm.get('vol', 1) <= 0: rm['vol'] = 1.0  # prevent skip
                bw, br, bt = find_best_passive_materials(
                    rm["temp"], rm["wall"], rm["roof"], rm["roof_proj"], rm["vol"],
                    wall_thickness, roof_thickness, h_in, h_out, wall_area, volume,
                    total_window_area, total_door_area, U_A_ventilation, Q_internal,
                    u_window, u_door, wd, MATERIALS
                )
                
                # Estimate windows and doors for this room proportionally
                room_vol_ratio = rm['vol'] / max(volume, 1e-6)
                room_win_area = total_window_area * room_vol_ratio
                room_door_area = total_door_area * room_vol_ratio
                
                num_windows = max(0, int(round(room_win_area / 1.8)))
                num_doors = max(0, int(round(room_door_area / 2.1)))
                
                three_data.append({
                    "id": f"r{idx+1}",
                    "name": rm.get('name', f"Room {idx+1}"),
                    "gx": float(rm.get('x', 0.0)),
                    "gy": -float(rm.get('y', 0.0)),
                    "x": float(rm.get('x', 0.0)),
                    "y": float(rm.get('y', 0.0)),
                    "l": float(rm.get('l', 5.0)),
                    "w": float(rm.get('w', 5.0)),
                    "h": float(rm.get('h', 3.0)),
                    "shape": rm.get('shape', 'Box'),
                    "rad": float(rm.get('rad', 3.0)),
                    "rot": float(rm.get('rot', 0.0)),
                    "wall": rm.get('wall_mat', 'Brick (Solid)'),
                    "roof": rm.get('roof_mat', 'Wood (Softwood)'),
                    "wall_mat": rm.get('wall_mat', 'Brick (Solid)'),
                    "roof_mat": rm.get('roof_mat', 'Wood (Softwood)'),
                    "ai_wall": bw,
                    "ai_roof": br,
                    "target_temp": float(rm.get('temp', optimal_temp)),
                    "passive_temp": float(bt),
                    "windows": num_windows,
                    "doors": num_doors,
                    "num_windows": num_windows,
                    "num_doors": num_doors
                })
                
            three_data_json = json.dumps(three_data)


            # ─── AI ROOM ARRANGEMENT OPTIMIZER ───────────────────────────────
            def optimize_room_arrangement(rooms, climate_hot):
                import math
                def heat_class(name):
                    n = name.lower()
                    if any(k in n for k in ['bed', 'sleep', 'office', 'study']): return 'stable'
                    if any(k in n for k in ['living', 'lounge', 'dining']): return 'warm'
                    if any(k in n for k in ['kitchen', 'cook']): return 'hot'
                    return 'buffer'
                zones = ['N', 'E', 'S', 'W']
                if climate_hot:
                    zone_score = {'N': 4, 'E': 3, 'W': 2, 'S': 1}
                else:
                    zone_score = {'S': 4, 'E': 3, 'W': 2, 'N': 1}
                class_zone_pref = {
                    'stable': ['N','E'] if climate_hot else ['S','E'],
                    'warm':   ['S','E'] if not climate_hot else ['N','W'],
                    'hot':    ['N','W'] if climate_hot else ['E','W'],
                    'buffer': ['W','N'] if climate_hot else ['N','W'],
                }
                used_zones = {}
                result = {}
                sorted_rooms = sorted(rooms, key=lambda r: ['stable','warm','hot','buffer'].index(heat_class(r['name'])))
                for rm in sorted_rooms:
                    hc = heat_class(rm['name'])
                    preferred = class_zone_pref[hc]
                    assigned = None
                    for z in preferred:
                        if used_zones.get(z, 0) < 2:
                            assigned = z
                            used_zones[z] = used_zones.get(z, 0) + 1
                            break
                    if assigned is None:
                        for z in zones:
                            if used_zones.get(z, 0) < 2:
                                assigned = z; used_zones[z] = used_zones.get(z,0)+1; break
                    if assigned is None:
                        assigned = zones[0]
                    base_wwr = {'stable': 0.25, 'warm': 0.35, 'hot': 0.20, 'buffer': 0.10}
                    wwr = base_wwr[hc]
                    if climate_hot and assigned == 'S': wwr = max(0.10, wwr - 0.10)
                    if not climate_hot and assigned == 'N': wwr = max(0.10, wwr - 0.10)
                    if rm['shape'] == 'Box':
                        wall_area_for_windows = (rm['l'] + rm['w']) * rm['h']
                    else:
                        wall_area_for_windows = 2 * math.pi * rm.get('rad', 3) * rm['h'] * 0.5
                    window_area = wwr * wall_area_for_windows
                    rec_windows = max(1, round(window_area / 1.2))
                    zone_color = {'N': '#4fc3f7', 'S': '#ef5350', 'E': '#ffa726', 'W': '#66bb6a'}
                    energy_save_pct = zone_score[assigned] * 3
                    result[rm['id']] = {
                        'zone': assigned,
                        'heat_class': hc,
                        'wwr': round(wwr, 2),
                        'rec_windows': rec_windows,
                        'rec_doors': 1,
                        'zone_color': zone_color[assigned],
                        'energy_save_pct': energy_save_pct,
                    }
                return result

            _wd_safe = st.session_state.get('weather_data', {})
            avg_t = 30
            try:
                _wd_vals = _wd_safe.get('T2M_MAX', None)
                if _wd_vals is not None and len(_wd_vals) > 0:
                    avg_t = float(list(_wd_vals.values())[0]) if isinstance(_wd_vals, dict) else float(_wd_vals[0])
            except Exception:
                avg_t = 30
            climate_is_hot = float(avg_t) > 24
            ai_arrangement = optimize_room_arrangement(three_data, climate_is_hot)
            for td in three_data:
                opt = ai_arrangement.get(td['id'], {})
                td['ai_zone']         = opt.get('zone', 'N')
                td['ai_zone_color']   = opt.get('zone_color', '#888888')
                td['ai_heat_class']   = opt.get('heat_class', 'stable')
                td['ai_wwr']          = opt.get('wwr', 0.25)
                td['ai_rec_windows']  = opt.get('rec_windows', 2)
                td['ai_rec_doors']    = opt.get('rec_doors', 1)
                td['ai_energy_save']  = opt.get('energy_save_pct', 5)
            # ─────────────────────────────────────────────────────────────────

            import json
            m_colors = {
                "Brick (Solid)": 0x9c4a2e,
                "Concrete (Standard)": 0x7c7f82,
                "Wood (Softwood)": 0xc79a5b,
                "Glass (Single Pane)": 0xadd8e6,
                "Glass (Double Pane)": 0x8fd0e8,
                "Steel (Standard)": 0x6c7a89,
                "EPS Insulation": 0xe9e6d8,
                "Straw Bale": 0xdaa520,
                "Adobe/Earth": 0xa0522d,
                "Stone (Granite/Limestone)": 0x696969
            }
            m_colors = {
                "Brick (Solid)": 0x9c4a2e,
                "Brick (Hollow)": 0xbd6243,
                "Concrete (Standard)": 0x7c7f82,
                "Concrete (Aerated)": 0x9fa3a6,
                "Wood (Softwood)": 0xc79a5b,
                "Wood (Hardwood)": 0x8b5a2b,
                "Glass (Single Pane)": 0xadd8e6,
                "Glass (Double Pane)": 0x8fd0e8,
                "Steel (Galvanized)": 0x6c7a89,
                "Aluminum (Sheet)": 0xa8b4c0,
                "EPS Insulation": 0xe9e6d8,
                "SIPs (Insulated Panels)": 0xe9e6d8,
                "Straw Bale": 0xdaa520,
                "Adobe / Mudbrick": 0xa0522d,
                "Rammed Earth": 0x8f5a3c,
                "Stone (Granite/Marble)": 0x5c6166,
                "Bamboo": 0x7a9a5b
            }
            mats_js = {}
            for m_name, m_props in MATERIALS.items():
                u_val = float(m_props.get("u_value", 1.0))
                dens = float(m_props.get("density", 1800))
                cost_kg = float(m_props.get("cost_per_kg", 0.5))
                # Conductivity k ~ u * d (est 0.2m wall)
                k_val = round(u_val * 0.2, 2)
                r_val = round(1.0 / max(u_val, 0.01), 2)
                cost_sqm = round(cost_kg * dens * 0.2 * 0.1, 1) + 15.0

                mat_entry = {
                    "name": m_name,
                    "color": m_colors.get(m_name, 0x7c7f82),
                    "conductivity": k_val,
                    "density": dens,
                    "rvalue": r_val,
                    "cost": cost_sqm,
                    "u_value": u_val,
                    "gwp": float(m_props.get("gwp", 0.0))
                }
                mats_js[m_name] = mat_entry
                # Also add clean short aliases
                short_k = m_name.split("(")[0].strip().lower()
                mats_js[short_k] = mat_entry

            # Add default template keys
            mats_js["timber"] = mats_js.get("wood", mats_js.get("Wood (Softwood)"))
            mats_js["brick"] = mats_js.get("Brick (Solid)")
            mats_js["concrete"] = mats_js.get("Concrete (Standard)")
            mats_js["glass_double"] = mats_js.get("Glass (Double Pane)")
            mats_js["steel_panel"] = mats_js.get("Steel (Galvanized)")
            mats_js["clay_tile"] = mats_js.get("Brick (Solid)")
            mats_js["eps"] = mats_js.get("EPS Insulation", mats_js.get("SIPs (Insulated Panels)"))
            mats_js["slate"] = mats_js.get("Stone (Granite/Marble)")
            mats_js["green_roof"] = mats_js.get("Straw Bale")

            materials_json = json.dumps(mats_js)
            
            # Using replacement on a raw string to avoid f-string {} brace escaping issues with CSS/JS

            if not three_data:
                st.info("Configure your rooms in Tab 2 first, then come back here to see the 3D simulation.")
            else:
                with open("ai_floor_plan.html", "r", encoding="utf-8") as _f:
                    _html_tmpl = _f.read()
                # Use split-based injection to avoid JSON brace collisions
                _parts_m = _html_tmpl.split("MATERIALS_PLACEHOLDER")
                _html_tmpl2 = materials_json.join(_parts_m)
                _parts_r = _html_tmpl2.split("ROOMS_PLACEHOLDER")
                html_code = three_data_json.join(_parts_r)
                components.html(html_code, height=800, scrolling=False)
