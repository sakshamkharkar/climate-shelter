import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import datetime
import plotly.graph_objects as go
import numpy as np
import pandas as pd

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
st.title("Shelter Weather Analyzer & 3D Thermodynamics")

tab1, tab2 = st.tabs(["1. Map & Weather Data", "2. 3D Design & Thermodynamics"])

# --- TAB 1: Map & Weather ---
with tab1:
    st.write("Click on the map to pinpoint a location, then click **Analyze Weather**.")
    col1, col2 = st.columns([2, 1])

    with col1:
        m = folium.Map(
            location=[20.5937, 78.9629], 
            zoom_start=5,
            tiles="https://mt1.google.com/vt/lyrs=m&gl=IN&hl=en-IN&x={x}&y={y}&z={z}",
            attr="Google Maps (India)"
        )
        folium.LatLngPopup().add_to(m)
        st_data = st_folium(m, height=500, width=800)

    with col2:
        st.subheader("Location Selection")
        
        if "lat" not in st.session_state:
            st.session_state.lat = 20.5937
        if "lon" not in st.session_state:
            st.session_state.lon = 78.9629
        if "last_map_click" not in st.session_state:
            st.session_state.last_map_click = None
            
        if st_data and st_data.get("last_clicked") != st.session_state.last_map_click:
            st.session_state.last_map_click = st_data["last_clicked"]
            st.session_state.lat = st_data["last_clicked"]["lat"]
            st.session_state.lon = st_data["last_clicked"]["lng"]
            
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
    if "weather_data" not in st.session_state:
        st.warning("Please analyze weather data in Tab 1 first.")
    else:
        st.header("Shelter Design & Energy Simulator")
        
        col_design, col_viz = st.columns([1, 2])
        
        with col_design:
            st.subheader("Target Environment")
            optimal_temp = st.slider("Target Indoor Temp (°C)", 10.0, 30.0, 21.0)
            
            st.subheader("Structure Shape")
            build_mode = st.radio("Building Type", ["Single Shape", "Compound Structure (Base + Roof)", "Multi-Room (Modular)"])
            
            area = 0
            roof_area = 0
            volume = 0
            floor_area = 0
            
            fig = go.Figure()
            
            # --- 3D Drawing Helpers ---
            def draw_box(fig, l, w, h, z_offset=0, x_offset=0):
                x = [0, l, l, 0, 0, 0, l, l, 0, 0, l, l, 0, 0, l, l]
                x = [val + x_offset for val in x]
                y = [0, 0, w, w, 0, 0, 0, w, w, 0, 0, 0, w, w, w, w]
                z = [z_offset, z_offset, z_offset, z_offset, z_offset, h+z_offset, h+z_offset, h+z_offset, h+z_offset, h+z_offset, h+z_offset, z_offset, z_offset, h+z_offset, h+z_offset, z_offset]
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='blue', width=4)))
            
            def draw_cylinder(fig, r, h, z_offset=0, x_offset=0):
                u = np.linspace(0, 2 * np.pi, 30)
                x_c = r * np.cos(u) + r + x_offset 
                y_c = r * np.sin(u) + r
                fig.add_trace(go.Scatter3d(x=x_c, y=y_c, z=np.zeros_like(u)+z_offset, mode='lines', line=dict(color='blue')))
                fig.add_trace(go.Scatter3d(x=x_c, y=y_c, z=np.ones_like(u)*h+z_offset, mode='lines', line=dict(color='blue')))
                for i in range(0, len(u), 5):
                    fig.add_trace(go.Scatter3d(x=[x_c[i], x_c[i]], y=[y_c[i], y_c[i]], z=[z_offset, h+z_offset], mode='lines', line=dict(color='blue')))
            
            def draw_dome(fig, r, z_offset=0, x_offset=0):
                u = np.linspace(0, 2 * np.pi, 30)
                v = np.linspace(0, np.pi / 2, 15)
                x = r * np.outer(np.cos(u), np.sin(v)).flatten() + r + x_offset
                y = r * np.outer(np.sin(u), np.sin(v)).flatten() + r
                z = r * np.outer(np.ones(np.size(u)), np.cos(v)).flatten() + z_offset
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=2, color='blue')))
                
            def draw_a_frame(fig, l, w, h, z_offset=0, x_offset=0):
                x = [0, l, l, 0, 0, 0, l, l, 0, l]
                x = [val + x_offset for val in x]
                y = [0, 0, w, w, 0, w/2, w/2, 0, w, w/2]
                z = [z_offset, z_offset, z_offset, z_offset, z_offset, h+z_offset, h+z_offset, z_offset, z_offset, h+z_offset]
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='blue', width=4)))
                
            def draw_pyramid_roof(fig, l, w, h, z_offset=0, x_offset=0):
                x = [0, l, l, 0, 0, l/2, l, l/2, 0, l/2, l]
                x = [val + x_offset for val in x]
                y = [0, 0, w, w, 0, w/2, 0, w/2, w, w/2, w]
                z = [z_offset, z_offset, z_offset, z_offset, z_offset, h+z_offset, z_offset, h+z_offset, z_offset, h+z_offset, z_offset]
                fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='blue', width=4)))

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
                wall_area = 0
                roof_surface_area = 0
                roof_area = 0
                floor_area = 0
                volume = 0
                
                current_x = 0
                prev_w = 0
                prev_h = 0
                prev_shape = None
                
                for i in range(num_rooms):
                    st.markdown(f"**Room {i+1}**")
                    r_shape = st.selectbox(f"Shape - Room {i+1}", ["Box", "Dome", "Triangular (A-Frame)", "Cylinder"], key=f"shape_{i}")
                    
                    r_l, r_w, r_h = 0, 0, 0
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
                        draw_box(fig, r_l, r_w, r_h, x_offset=current_x)
                        
                    elif r_shape == "Dome":
                        r_radius = st.number_input("Radius (m)", 2.0, 15.0, 5.0, key=f"rad_{i}")
                        r_l = r_radius * 2
                        r_w = r_radius * 2
                        r_h = r_radius
                        room_wall_area = 0
                        r_surface = 2 * np.pi * r_radius**2
                        r_roof_area = np.pi * r_radius**2
                        r_volume = (2/3) * np.pi * r_radius**3
                        draw_dome(fig, r_radius, x_offset=current_x)
                        
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
                        draw_a_frame(fig, r_l, r_w, r_h, x_offset=current_x)
                        
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
                        draw_cylinder(fig, r_radius, r_h, x_offset=current_x)
                    
                    if i > 0:
                        shared_w = min(r_w, prev_w)
                        shared_h = min(r_h, prev_h)
                        if r_shape in ["Dome", "Cylinder"] or prev_shape in ["Dome", "Cylinder"]:
                            shared_area = min(shared_w * shared_h * 0.2, 4.0) 
                        else:
                            shared_area = shared_w * shared_h
                        wall_area -= shared_area * 2 
                        
                    wall_area += room_wall_area
                    roof_surface_area += r_surface
                    roof_area += r_roof_area
                    floor_area += r_l * r_w
                    volume += r_volume
                    
                    current_x += r_l 
                    prev_w = r_w
                    prev_h = r_h
                    prev_shape = r_shape

            # --- DOORS & WINDOWS ---
            st.subheader("Doors & Windows")
            
            c1, c2 = st.columns(2)
            with c1:
                num_doors = st.number_input("Number of Doors", 0, 10, 1)
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
                num_windows = st.number_input("Number of Windows", 0, 20, 2)
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
            wall_thickness = st.slider("Wall/Roof Thickness (m)", 0.05, 0.5, 0.2, step=0.01)
            
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
            st.subheader("3D Wireframe")
            
            if num_doors > 0:
                fig.add_trace(go.Scatter3d(x=[0, d_w, d_w, 0, 0], y=[-0.1, -0.1, -0.1, -0.1, -0.1], z=[0, 0, d_h, d_h, 0], mode='lines', line=dict(color='red', width=6), name="Door Area"))
            if num_windows > 0:
                fig.add_trace(go.Scatter3d(x=[0, w_w, w_w, 0, 0], y=[-0.1, -0.1, -0.1, -0.1, -0.1], z=[d_h+0.5, d_h+0.5, d_h+0.5+w_h, d_h+0.5+w_h, d_h+0.5], mode='lines', line=dict(color='green', width=4), name="Window Area"))
                
            fig.update_layout(scene=dict(aspectmode="data"), margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

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
            
        st.markdown("---")
        
        # --- PASSIVE INDOOR TEMPERATURE MODEL ---
        st.header("🌡️ Passive Indoor Temperature (No AC/Heating)")
        st.write("Calculates natural indoor temperatures using strict exponential thermal mass decay (τ), wind-driven convection, and deep space radiative cooling.")
        
        st.markdown("---")
        st.header("Passive Indoor Temperature Prediction")
        
        wd = st.session_state.weather_data
        
        # 1. Base Assumptions
        capacity = volume * 1.2 * 1000 # J/K (Air heat capacity)
        
        k_wall = u_wall * 0.2
        k_roof = u_roof * 0.2
        
        wind_m_s = wd.get("avg_wind", 10.0) * (1000/3600)
        
        h_out = 5.7 + 3.8 * wind_m_s  # External convective heat transfer
        h_in = 8.0  # Internal convective heat transfer
        
        # True U-value = 1 / (R_in + R_cond + R_out)
        true_u_wall = 1 / ((1/h_in) + (wall_thickness / k_wall) + (1/h_out))
        true_u_roof = 1 / ((1/h_in) + (wall_thickness / k_roof) + (1/h_out))
        
        # Base Envelope Heat Transfer (W/K)
        U_A_conductive = (true_u_wall * solid_wall_area) + (true_u_roof * roof_surface_area) + (u_window * total_window_area) + (u_door * total_door_area)
        
        # 2. Wind Ventilation Heat Transfer (W/K)
        effective_open_area = total_window_area * 0.1
        airflow = effective_open_area * wind_m_s * 0.5
        U_A_ventilation = airflow * 1200
        
        U_A = U_A_conductive + U_A_ventilation
        if U_A == 0: U_A = 0.1 
        
        # 3. Heat Gains (Solar & Internal)
        Q_internal = capacity * 100 
        solar_radiance_w_m2 = wd["avg_solar_mj"] * 11.57
        Q_solar_roof = solar_radiance_w_m2 * roof_area * abs_roof
        
        Q_solar_avg = Q_solar_roof
        Q_solar_peak = Q_solar_avg * 2.5
        
        # 4. Thermal Mass (τ) Calculation
        cp_dict = {
            "Concrete (Standard)": 840, "Concrete (Aerated)": 1000, "Brick (Solid)": 840,
            "Brick (Hollow)": 840, "Wood (Softwood)": 1600, "Wood (Hardwood)": 1600,
            "Steel (Galvanized)": 450, "Aluminum (Sheet)": 900, "Adobe / Mudbrick": 1000,
            "Rammed Earth": 1000, "Straw Bale": 2000, "SIPs (Insulated Panels)": 1400,
            "Stone (Granite/Marble)": 800, "Bamboo": 1600
        }
        cp_wall = cp_dict.get(wall_material, 1000)
        
        # tau = (rho * cp * L^2) / k
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
        
        # Night temperature decay (8 hours after sunset) using exponential time constant
        night_hours = 8.0
        decay_factor = np.exp(-night_hours / max(tau_hours, 0.1))
        
        t_in_min_undamped = T_night_baseline + (Q_internal / U_A)
        t_in_min = t_in_min_undamped + (delta_t_day * decay_factor)
        
        daytime_dampening = 1.0 - np.exp(-12.0 / max(tau_hours, 0.1))
        t_in_max = t_in_avg + (t_in_max_undamped - t_in_avg) * daytime_dampening
        
        t1, t2, t3 = st.columns(3)
        t1.metric("Avg Indoor Temp", f"{t_in_avg:.1f} °C", f"{t_in_avg - wd['avg_temp']:+.1f} °C vs Outdoor Avg", delta_color="off")
        t2.metric("Extreme Max Indoor", f"{t_in_max:.1f} °C", f"{t_in_max - wd['ext_max']:+.1f} °C vs Outdoor Max", delta_color="inverse")
        t3.metric("Extreme Min (Night) Temp", f"{t_in_min:.1f} °C", f"{t_in_min - wd['ext_min']:+.1f} °C vs Outdoor Min", delta_color="normal")
        
        st.caption(f"**Physics Diagnostics:** Thermal Time Constant (τ) = **{tau_hours:.1f} hours**. Natural Ventilation Heat Transfer = **{U_A_ventilation:,.0f} W/K** (driven by {wd.get('avg_wind', 0):.1f} km/h local wind).")

        st.markdown("---")
        st.header(f"⚡ Active HVAC Energy Analysis (Target: {optimal_temp}°C)")
        
        delta_t = abs(wd["avg_temp"] - optimal_temp)
        heat_loss_w = U_A * delta_t
        heat_loss_kwh_yr = (heat_loss_w * 24 * 365) / 1000
        
        solar_gain_w = Q_solar_avg
        solar_gain_kwh_yr = (solar_gain_w * 24 * 365) / 1000
        
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
            
        st.subheader(f"Ökobaudat Wall Material Comparison (Keeping {roof_material} Roof)")
        comp_data = []
        
        for m_name, m_props in MATERIALS.items():
            m_k_wall = m_props["u_value"] * 0.2
            m_true_u_wall = 1 / ((1/h_in) + (wall_thickness / m_k_wall) + (1/h_out))
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
        }), use_container_width=True)
        
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
        
        st.success(f"💰 **Most Cost-Efficient Wall Material:** {best_cost_mat} (₹{best_cost_val:,.0f})")
        
        if cost_savings > 0:
            st.info(f"💵 **Cost Savings:** Using **{best_cost_mat}** instead of your selected **{wall_material}** saves **₹{cost_savings:,.0f} ({cost_savings_pct:.1f}%)** in material costs for the walls!")
        else:
            st.info(f"💵 **Cost Savings:** Your selected **{wall_material}** is already the most cost-efficient option for the walls!")
        
        st.info(f"🧭 **Best Orientation:** {best_orient}")
        st.info(f"⚡ **Energy Savings:** Using {best_mat} instead of Standard Concrete saves **{savings:.1f}%** in energy waste per year to maintain {optimal_temp}°C!")
