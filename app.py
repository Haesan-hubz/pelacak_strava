import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")
st.title("🗺️ Navigasi Rute Strava (Live Real-Time)")
st.write("Bawa HP Anda berjalan, peta akan otomatis bergeser mengikuti langkah Anda tanpa refresh manual.")

# =========================================================================
# 1. ENGINE UTAMA: CAPTURE SENSOR LOKASI HP (REAL-TIME)
# =========================================================================
js_gps_code = """
new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
        resolve({error: "Browser tidak mendukung GPS"});
    }
    navigator.geolocation.getCurrentPosition(
        (position) => {
            resolve({
                lat: position.coords.latitude,
                lon: position.coords.longitude,
                accuracy: position.coords.accuracy
            });
        },
        (error) => { resolve({error: error.message}); },
        { enableHighAccuracy: true, maximumAge: 0, timeout: 4000 }
    );
});
"""


# Mengambil koordinat perangkat saat ini
data_gps = streamlit_js_eval(js_expressions=js_gps_code, key="watch_gps")

# Tombol untuk Upload File Rute .GPX Strava
file_gpx = st.file_uploader("Upload Rute Panduan (.gpx)", type=["gpx"])

# =========================================================================
# 2. PROSES PETA DAN NAVIGASI DI DALAM FRAGMENT (PENYEGARAN OTOMATIS)
# =========================================================================
if file_gpx is not None:
    gpx = gpxpy.parse(file_gpx)
    titik_rute = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                titik_rute.append([point.latitude, point.longitude])
                
    if titik_rute:
        # Tentukan titik awal rute Strava sebagai default
        pusat_peta = titik_rute[0]
        
        # Simpan koordinat live ke dalam memori session state
        if data_gps and isinstance(data_gps, dict) and "lat" in data_gps:
            st.session_state.lat_live = data_gps["lat"]
            st.session_state.lon_live = data_gps["lon"]
            st.session_state.accuracy = data_gps["accuracy"]
            pusat_peta = [st.session_state.lat_live, st.session_state.lon_live]
            
            st.sidebar.success(
                f"Sinyal GPS Terkunci! 📍\n"
                f"Lat: {st.session_state.lat_live:.5f}\n"
                f"Lon: {st.session_state.lon_live:.5f}\n"
                f"Akurasi: {st.session_state.accuracy:.1f} m"
            )
        else:
            st.sidebar.warning("Sedang mencari sinyal GPS HP... Pastikan Anda berjalan di luar ruangan.")

        # Membuat Peta Interaktif
        peta = folium.Map(location=pusat_peta, zoom_start=17)
        
        # GAMBAR JALUR PANDUAN: Rute dari Strava (Garis Oranye)
        folium.PolyLine(titik_rute, color="#fc4c02", weight=6, opacity=0.8).add_to(peta)
        folium.Marker(titik_rute[0], popup="Start", icon=folium.Icon(color="green", icon="play")).add_to(peta)
        folium.Marker(titik_rute[-1], popup="Finish", icon=folium.Icon(color="black", icon="flag")).add_to(peta)
        
        # GAMBAR POSISI LIVE: Titik Biru yang otomatis berpindah
        if "lat_live" in st.session_state:
            folium.Marker(
                [st.session_state.lat_live, st.session_state.lon_live],
                popup="Posisi Anda Sekarang",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(peta)
        
        # Tampilkan peta ke layar browser HP
        st_folium(peta, width=900, height=600, key="peta_navigasi_live")
        
        # Pemicu Rerun otomatis khusus untuk memperbarui sensor GPS setiap 4 detik
        time_trigger = st.checkbox("Aktifkan Pelacakan Otomatis (Live Tracking)", value=True)
        if time_trigger:
            import time
            time.sleep(4)
            st.rerun() # Memaksa Streamlit membaca ulang sensor koordinat baru
            
    else:
        st.error("File GPX tidak valid.")
