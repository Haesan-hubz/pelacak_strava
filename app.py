import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.set_page_config(layout="wide")
st.title("bismmilah mboten error")
st.write("gek ndang, pingin turu aku")

file_gpx = st.file_uploader("Upload Rute Panduan (.gpx)", type=["gpx"])

lokasi_live = get_geolocation()

if file_gpx is not None:
    
    gpx = gpxpy.parse(file_gpx)
    titik_rute = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                titik_rute.append([point.latitude, point.longitude])
                
    if titik_rute:
        pusat_peta = titik_rute[0] 
        
        if lokasi_live:
            lat_live = lokasi_live['coords']['latitude']
            lon_live = lokasi_live['coords']['longitude']
            pusat_peta = [lat_live, lon_live]
            st.sidebar.success(f"GPS Perangkat Aktif! 📍\nLat: {lat_live:.5f}\nLon: {lon_live:.5f}")
        else:
            st.sidebar.warning("Sedang mencari sinyal GPS HP... Pastikan izin lokasi browser Anda aktif.")

        peta = folium.Map(location=pusat_peta, zoom_start=16)
        
        folium.PolyLine(titik_rute, color="#fc4c02", weight=6, opacity=0.8, popup="Rute Target").add_to(peta)
        
        folium.Marker(titik_rute[0], popup="Start Rute", icon=folium.Icon(color="green", icon="play")).add_to(peta)
        folium.Marker(titik_rute[-1], popup="Finish Rute", icon=folium.Icon(color="black", icon="flag")).add_to(peta)
        
        if lokasi_live:
            folium.Marker(
                [lat_live, lon_live],
                popup="Posisi Anda Sekarang",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(peta)
        
        st_folium(peta, width=900, height=600, key="peta_navigasi")
        
    else:
        st.error("File GPX tidak valid atau tidak memiliki data koordinat.")
