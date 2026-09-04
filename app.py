import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.set_page_config(layout="wide")
st.title("bismmilah mboten error")
st.write("gek ndang, pingin turu aku")

# Tombol untuk Upload File Rute .GPX Strava
file_gpx = st.file_uploader("Upload Rute Panduan (.gpx)", type=["gpx"])

# Ambil Lokasi Real-Time dari GPS HP Pengguna
lokasi_live = get_geolocation()

if file_gpx is not None:
    # Membaca data dari file GPX yang di-upload
    gpx = gpxpy.parse(file_gpx)
    titik_rute = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                titik_rute.append([point.latitude, point.longitude])
                
    if titik_rute:
        # --- PERBAIKAN DI SINI ---
        # Default pusat peta diambil dari koordinat PERTAMA (titik awal rute), bukan seluruh list
        pusat_peta = titik_rute[0] 
        
        # Jika GPS HP merespon dan mendeteksi koordinat Anda, geser pusat peta ke posisi Anda
        if lokasi_live:
            lat_live = lokasi_live['coords']['latitude']
            lon_live = lokasi_live['coords']['longitude']
            pusat_peta = [lat_live, lon_live]
            st.sidebar.success(f"GPS Perangkat Aktif! 📍\nLat: {lat_live:.5f}\nLon: {lon_live:.5f}")
        else:
            st.sidebar.warning("Sedang mencari sinyal GPS HP... Pastikan izin lokasi browser Anda aktif.")

        # Membuat Objek Peta Interaktif dengan koordinat pusat yang benar
        peta = folium.Map(location=pusat_peta, zoom_start=16)
        
        # GAMBAR JALUR PANDUAN: Rute dari Strava (Garis Oranye Khas Strava)
        folium.PolyLine(titik_rute, color="#fc4c02", weight=6, opacity=0.8, popup="Rute Target").add_to(peta)
        
        # Penanda Titik Start (menggunakan koordinat pertama) & Finish (koordinat terakhir)
        folium.Marker(titik_rute[0], popup="Start Rute", icon=folium.Icon(color="green", icon="play")).add_to(peta)
        folium.Marker(titik_rute[-1], popup="Finish Rute", icon=folium.Icon(color="black", icon="flag")).add_to(peta)
        
        # GAMBAR POSISI LIVE: Titik Biru Pengguna yang Sedang Berjalan
        if lokasi_live:
            folium.Marker(
                [lat_live, lon_live],
                popup="Posisi Anda Sekarang",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(peta)
        
        # Tampilkan Peta Terintegrasi ke Layar Browser
        st_folium(peta, width=900, height=600, key="peta_navigasi")
        
    else:
        st.error("File GPX tidak valid atau tidak memiliki data koordinat.")
