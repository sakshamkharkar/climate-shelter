import customtkinter as ctk
import tkintermapview
import requests
import statistics

# Create the main window
app = ctk.CTk()
app.geometry("1000x700")
app.title("Shelter Weather Analyzer")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Layout
frame_left = ctk.CTkFrame(master=app, width=300, corner_radius=0)
frame_left.pack(side="left", fill="y", padx=0, pady=0)

frame_right = ctk.CTkFrame(master=app)
frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Left Frame - Info & Results
lbl_title = ctk.CTkLabel(master=frame_left, text="Shelter Analyzer", font=("Roboto", 24, "bold"))
lbl_title.pack(pady=20, padx=20)

lbl_lat_lon = ctk.CTkLabel(master=frame_left, text="Right-click on map to pick location.", wraplength=250)
lbl_lat_lon.pack(pady=10, padx=20)

txt_results = ctk.CTkTextbox(master=frame_left, width=260, height=400)
txt_results.pack(pady=10, padx=20)
txt_results.insert("0.0", "Results will appear here.")
txt_results.configure(state="disabled")

btn_analyze = ctk.CTkButton(master=frame_left, text="Analyze Weather", state="disabled")
btn_analyze.pack(pady=20, padx=20)

# Right Frame - Map
map_widget = tkintermapview.TkinterMapView(frame_right, corner_radius=10)
map_widget.pack(fill="both", expand=True)
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&gl=IN&hl=en-IN&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
map_widget.set_position(20.5937, 78.9629) # default India
map_widget.set_zoom(5)

selected_coords = None
current_marker = None

def add_marker_event(coords):
    global current_marker, selected_coords
    if current_marker:
        current_marker.delete()
    current_marker = map_widget.set_marker(coords[0], coords[1], text="Selected")
    selected_coords = coords
    lbl_lat_lon.configure(text=f"Lat: {coords[0]:.4f}\nLon: {coords[1]:.4f}")
    btn_analyze.configure(state="normal")

map_widget.add_right_click_menu_command(label="Select Location", command=add_marker_event, pass_coords=True)

def analyze_weather():
    if not selected_coords:
        return
    
    lat, lon = selected_coords
    
    txt_results.configure(state="normal")
    txt_results.delete("0.0", "end")
    txt_results.insert("0.0", "Fetching data from open-meteo...\n")
    txt_results.configure(state="disabled")
    
    app.update()
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    # we take a recent past year for full data
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "daily" not in data:
            raise Exception("No daily data found in response. " + str(data.get('reason', '')))
        
        daily = data["daily"]
        t_max = [v for v in daily["temperature_2m_max"] if v is not None]
        t_min = [v for v in daily["temperature_2m_min"] if v is not None]
        precip = [v for v in daily["precipitation_sum"] if v is not None]
        
        avg_t_max = sum(t_max) / len(t_max) if t_max else 0
        avg_t_min = sum(t_min) / len(t_min) if t_min else 0
        avg_precip = sum(precip) / len(precip) if precip else 0
        
        ext_max = max(t_max) if t_max else 0
        ext_min = min(t_min) if t_min else 0
        total_precip = sum(precip)
        
        result_str = (
            f"--- 2020 Weather Data ---\n"
            f"Avg Max Temp: {avg_t_max:.1f}°C\n"
            f"Avg Min Temp: {avg_t_min:.1f}°C\n"
            f"Extreme Max Temp: {ext_max:.1f}°C\n"
            f"Extreme Min Temp: {ext_min:.1f}°C\n"
            f"Avg Daily Precip: {avg_precip:.1f}mm\n"
            f"Total Yearly Precip: {total_precip:.1f}mm\n\n"
            f"--- Shelter Build Analysis ---\n"
        )
        
        # simple rule-based analysis
        if ext_max > 35:
            result_str += "- Extreme Heat Detected! Shelter needs significant cooling/ventilation and heat insulation.\n"
        elif avg_t_max > 25:
            result_str += "- Warm Climate. Good ventilation is recommended.\n"
            
        if ext_min < 0:
            result_str += "- Freezing Temperatures Detected! Shelter MUST have heating and thick insulation to prevent pipes freezing and keep occupants warm.\n"
        elif avg_t_min < 10:
            result_str += "- Cold Climate. Basic heating and insulation needed.\n"
            
        if total_precip > 1500:
            result_str += "- Heavy Rainfall! Ensure a sloped roof, deep drainage, and waterproofing.\n"
        elif total_precip < 200:
            result_str += "- Arid/Dry Climate. Rainwater harvesting is highly recommended.\n"
        else:
            result_str += "- Moderate Rainfall. Standard roof slope is sufficient.\n"
            
        txt_results.configure(state="normal")
        txt_results.delete("0.0", "end")
        txt_results.insert("0.0", result_str)
        txt_results.configure(state="disabled")

    except Exception as e:
        txt_results.configure(state="normal")
        txt_results.delete("0.0", "end")
        txt_results.insert("0.0", f"Error fetching data:\n{e}")
        txt_results.configure(state="disabled")

btn_analyze.configure(command=analyze_weather)

app.mainloop()
