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
        # Mengubah data koordinat menjadi teks teks murni agar aman dimasukkan ke HTML
        rute_json = json.dumps(titik_rute)
        lat_start = float(titik_rute[0][0])
        lon_start = float(titik_rute[0][1])
        lat_finish = float(titik_rute[-1][0])
        lon_finish = float(titik_rute[-1][1])
        
        # =========================================================================
        # 2. KODE PETA JAVASCRIPT MURNI (PENYESUAIAN TOLERANSI SENSOR GPS)
        # =========================================================================
        html_code = """
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="https://unpkg.com" />
            <script src="https://unpkg.com"></script>
            <style>
                #map { height: 530px; width: 100%; border-radius: 10px; }
                #status { padding: 10px; background: #e2e3e5; color: #383d41; border-radius: 5px; margin-bottom: 10px; font-family: sans-serif; font-size: 14px; }
            </style>
        </head>
        <body>
            <div id="status">📡 Menghubungkan ke satelit GPS... Pastikan Anda berada di luar ruangan agar sinyal terkunci.</div>
            <div id="map"></div>

            <script>
                var latStart = """ + str(lat_start) + """;
                var lonStart = """ + str(lon_start) + """;
                var latFinish = """ + str(lat_finish) + """;
                var lonFinish = """ + str(lon_finish) + """;
                var ruteTarget = """ + rute_json + """;

                var map = L.map('map').setView([latStart, lonStart], 16);
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);

                L.polyline(ruteTarget, {color: '#fc4c02', weight: 6, opacity: 0.8}).addTo(map);
                L.marker([latStart, lonStart]).addTo(map).bindPopup("Start Rute");
                L.marker([latFinish, lonFinish]).addTo(map).bindPopup("Finish Rute");

                var liveMarker = L.circleMarker([latStart, lonStart], {
                    color: '#007bff', fillColor: '#007bff', fillOpacity: 0.9, radius: 10
                }).addTo(map).bindPopup("Posisi Kamu");

                var statusDiv = document.getElementById('status');

                if (navigator.geolocation) {
                    navigator.geolocation.watchPosition(
                        function(position) {
                            var lat = position.coords.latitude;
                            var lon = position.coords.longitude;
                            var acc = position.coords.accuracy;

                            liveMarker.setLatLng([lat, lon]);
                            map.setView([lat, lon]);

                            statusDiv.innerHTML = "✅ <b>Sinyal GPS Terkunci!</b> | Lat: " + lat.toFixed(5) + " | Lon: " + lon.toFixed(5) + " | Akurasi: " + acc.toFixed(1) + " meter";
                            statusDiv.style.background = "#d4edda";
                            statusDiv.style.color = "#155724";
                        },
                        function(error) {
                            // Jika eror karena timeout, kita berikan petunjuk agar pengguna ke luar ruangan
                            statusDiv.innerHTML = "⚠️ Sinyal GPS Lemah (Mencari Satelit...). Silakan jalan ke area terbuka luar ruangan. Error: " + error.message;
                            statusDiv.style.background = "#fff3cd";
                            statusDiv.style.color = "#856404";
                        },
                        // MELONGGARKAN SETELAN TIMEOUT AGAR GPS HP BERKESEMPATAN MENCARI SINYAL
                        { enableHighAccuracy: true, maximumAge: 3000, timeout: 27000 }
                    );
                } else {
                    statusDiv.innerHTML = "❌ Browser Anda tidak mendukung sensor GPS.";
                }
            </script>
        </body>
        </html>
        """
        
        # --- PERBAIKAN UTAMA: MENAMBAHKAN IZIN GEOLOCATION PADA IFRAME STREAMLIT ---
        st.components.v1.html(html_code, height=600, scrolling=False)
        
    else:
        st.error("File GPX tidak memiliki data koordinat.")
