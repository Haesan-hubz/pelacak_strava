import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")
st.title("🗺️ Navigasi Rute Strava (Live Real-Time)")
st.write("Bawa HP Anda berjalan, peta akan otomatis bergeser mengikuti langkah Anda tanpa refresh.")


js_gps_code = """
new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
        resolve({error: "Browser tidak mendukung GPS"});
    }
    navigator.geolocation.watchPosition(
        (position) => {
            resolve({
                lat: position.coords.latitude,
                lon: position.coords.longitude,
                accuracy: position.coords.accuracy
            });
        },
        (error) => { resolve({error: error.message}); },
        { enableHighAccuracy: true, maximumAge: 0, timeout: 5000 }
    );
});
"""

data_gps = streamlit_js_eval(js_expressions=js_gps_code, key="watch_gps")

file_gpx = st.file_uploader("Upload Rute Panduan (.gpx)", type=["gpx"])

if file_gpx is not None:
    gpx = gpxpy.parse(file_gpx)
    titik_rute = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                titik_rute.append([point.latitude, point.longitude])

    if titik_rute:
        pusat_peta = titik_rute

        if data_gps and isinstance(data_gps, dict) and "lat" in data_gps:
            lat_live = data_gps["lat"]
            lon_live = data_gps["lon"]
            pusat_peta = [lat_live, lon_live] # Peta otomatis berpusat ke posisi berjalan Anda
            st.sidebar.success(f"Sinyal GPS Terkunci! 📍\nLat: {lat_live:.5f}\nLon: {lon_live:.5f}\nAkurasi: {data_gps['accuracy']:.1f} meter")
        else:
            st.sidebar.warning("Sedang menghubungkan ke sensor pergerakan HP... Pastikan Anda berjalan di luar ruangan.")

        peta = folium.Map(location=pusat_peta, zoom_start=17)

        folium.PolyLine(titik_rute, color="#fc4c02", weight=6, opacity=0.8).add_to(peta)
        folium.Marker(titik_rute, popup="Start", icon=folium.Icon(color="green", icon="play")).add_to(peta)
        folium.Marker(titik_rute[-1], popup="Finish", icon=folium.Icon(color="black", icon="flag")).add_to(peta)


        if data_gps and isinstance(data_gps, dict) and "lat" in data_gps:
            folium.Marker(
                [lat_live, lon_live],
                popup="Posisi Anda Sekarang",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(peta)


        st_folium(peta, width=900, height=600, key="peta_navigasi_live")
    else:
        st.error("File GPX tidak valid.")
