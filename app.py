import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.set_page_config(layout="wide")
st.title("🏃‍♂️ Navigasi Rute Strava (Live Real-Time - FINAL)")
st.write("Bawa HP Anda berjalan di luar ruangan untuk mengikuti jalur.")

# 1. Tombol untuk Upload File Rute .GPX Strava
file_gpx = st.file_uploader("Upload Rute Panduan (.gpx)", type=["gpx"])

# 2. Ambil Lokasi Real-Time dari GPS Perangkat menggunakan Library Resmi
lokasi_live = get_geolocation()

if file_gpx is not None:
    # Membaca data koordinat rute dari file GPX
    gpx = gpxpy.parse(file_gpx)
    titik_rute = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                titik_rute.append([point.latitude, point.longitude])
                
    if titik_rute:
        # Default pusat peta diambil dari titik awal rute Strava
        pusat_peta = titik_rute[0]
        
        # Validasi jika GPS HP berhasil memberikan koordinat
        if lokasi_live and isinstance(lokasi_live, dict) and "coords" in lokasi_live:
            lat_live = lokasi_live['coords']['latitude']
            lon_live = lokasi_live['coords']['longitude']
            pusat_peta = [lat_live, lon_live] # Geser kamera peta ke posisi Anda
            
            st.success(
                f"✅ **Sinyal GPS Terkunci!** | Lat: {lat_live:.5f} | Lon: {lon_live:.5f} "
                f"| Akurasi: {lokasi_live['coords']['accuracy']:.1f} meter"
            )
        else:
            st.warning("📡 Sedang mencari sinyal GPS HP... Pastikan izin lokasi browser aktif dan Anda di luar ruangan.")
            # Tombol darurat untuk memaksa HP mencari ulang lokasi jika macet
            if st.button("🔄 Segarkan Lokasi Saya"):
                st.rerun()

        # 3. Membuat Objek Peta menggunakan Folium Resmi (Anti-Blokir)
        peta = folium.Map(location=pusat_peta, zoom_start=17)
        
        # GAMBAR JALUR PANDUAN: Rute dari Strava (Garis Oranye)
        folium.PolyLine(titik_rute, color="#fc4c02", weight=6, opacity=0.8).add_to(peta)
        folium.Marker(titik_rute[0], popup="Start", icon=folium.Icon(color="green", icon="play")).add_to(peta)
        folium.Marker(titik_rute[-1], popup="Finish", icon=folium.Icon(color="black", icon="flag")).add_to(peta)
        
        # GAMBAR POSISI LIVE: Titik Biru Posisi Anda
        if lokasi_live and "coords" in lokasi_live:
            folium.Marker(
                [lat_live, lon_live],
                popup="Posisi Anda Sekarang",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(peta)
        
        # Tampilkan peta secara aman ke layar browser HP
        st_folium(peta, width=900, height=550, key="peta_navigasi_final")
        
        # Otomatis memicu pembaruan koordinat setiap 7 detik secara aman tanpa merusak peta
        import time
        time.sleep(4)
        st.rerun()
        
    else:
        st.error("File GPX tidak memiliki data koordinat.")
