import streamlit as st
import gpxpy
import json

st.set_page_config(layout="wide")
st.title("🏃‍♂️ Navigasi Rute Strava (Live Real-Time - HTML5ke2)")
st.write("Bawa HP Anda berjalan di luar ruangan. Titik biru akan bergeser mulus secara live tanpa ada refresh halaman!")

# 1. Tombol untuk Upload File Rute .GPX Strava
file_gpx = st.file_uploader("Upload Rute Panduan (.gpx)", type=["gpx"])

if file_gpx is not None:
    # Membaca data koordinat rute dari file GPX
    gpx = gpxpy.parse(file_gpx)
    titik_rute = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                titik_rute.append([point.latitude, point.longitude])
                
    if titik_rute:
        # Mengubah data list Python menjadi format JSON agar bisa dibaca oleh JavaScript peta
        rute_json = json.dumps(titik_rute)
        lat_start = titik_rute[0][0]
        lon_start = titik_rute[0][1]
        lat_finish = titik_rute[-1][0]
        lon_finish = titik_rute[-1][1]
        
        # =========================================================================
        # 2. INJEKSI KODE PETA JAVASCRIPT MURNI (ANTI REFRESH / LIVE TRACKING)
        # =========================================================================
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="https://unpkg.com" />
            <script src="https://unpkg.com"></script>
            <style>
                #map {{ height: 550px; width: 100%; border-radius: 10px; }}
                #status {{ padding: 10px; background: #e2e3e5; color: #383d41; border-radius: 5px; margin-bottom: 10px; font-family: sans-serif; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div id="status">📡 Menghubungkan ke satelit GPS... Pastikan izin lokasi aktif dan Anda di luar ruangan.</div>
            <div id="map"></div>

            <script>
                // A. Inisialisasi Peta Dasar berpusat di titik awal Rute
                var map = L.map('map').setView([{lat_start}, {lon_start}], 16);
                
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);

                // B. Menggambar Garis Rute Panduan Strava (Oranye)
                var ruteTarget = {rute_json};
                L.polyline(ruteTarget, {{color: '#fc4c02', weight: 6, opacity: 0.8}}).addTo(map);
                
                // Penanda Start & Finish Rute
                L.marker([{lat_start}, {lon_start}]).addTo(map).bindPopup("Start Rute");
                L.marker([{lat_finish}, {lon_finish}]).addTo(map).bindPopup("Finish Rute");

                // C. Membuat Penanda Titik Biru Live Pengguna (Awalnya ditaruh di titik start rute)
                var liveMarker = L.circleMarker([{lat_start}, {lon_start}], {{
                    color: '#007bff', fillColor: '#007bff', fillOpacity: 0.9, radius: 10
                }}).addTo(map).bindPopup("Posisi Kamu");

                var statusDiv = document.getElementById('status');

                // D. FUNGSI INTI: Memantau Pergerakan Sensor GPS HP Tanpa Halaman Memuat Ulang
                if (navigator.geolocation) {{
                    navigator.geolocation.watchPosition(
                        function(position) {{
                            var lat = position.coords.latitude;
                            var lon = position.coords.longitude;
                            var acc = position.coords.accuracy;

                            // 1. Geser Titik Biru ke Posisi Baru di Peta
                            liveMarker.setLatLng([lat, lon]);
                            
                            // 2. Otomatis Geser Fokus Kamera Peta Mengikuti Langkah Anda
                            map.setView([lat, lon]);

                            // 3. Update Status Teks Akurasi GPS
                            statusDiv.innerHTML = "✅ <b>Sinyal GPS Terkunci!</b> | Lat: " + lat.toFixed(5) + " | Lon: " + lon.toFixed(5) + " | Akurasi: " + acc.toFixed(1) + " meter";
                            statusDiv.style.background = "#d4edda";
                            statusDiv.style.color = "#155724";
                        }},
                        function(error) {{
                            statusDiv.innerHTML = "❌ Gagal mengambil GPS: " + error.message;
                            statusDiv.style.background = "#f8d7da";
                            statusDiv.style.color = "#721c24";
                        }},
                        {{ enableHighAccuracy: true, maximumAge: 0, timeout: 5000 }}
                    );
                }} else {{
                    statusDiv.innerHTML = "❌ Browser Anda tidak mendukung sensor GPS.";
                }}
            </script>
        </body>
        </html>
        """
        
        # Tampilkan komponen peta HTML/JavaScript murni ke layar Streamlit
        st.components.v1.html(html_code, height=600)
        
    else:
        st.error("File GPX tidak memiliki data koordinat.")
