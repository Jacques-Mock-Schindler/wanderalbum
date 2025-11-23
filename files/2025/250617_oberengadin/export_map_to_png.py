"""
Exportiert die Folium-Karte als PNG-Datei.

Verwendung:
    python export_map_to_png.py [output_filename.png] [width] [height]
    
Beispiele:
    python export_map_to_png.py                          # Standardwerte: map_output.png, 1200x800
    python export_map_to_png.py wanderkarte.png          # Eigener Dateiname
    python export_map_to_png.py wanderkarte.png 1600 1000  # Eigene Größe
"""

import os
import sys
import time
import folium
import gpxpy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Kommandozeilenargumente verarbeiten
output_filename = sys.argv[1] if len(sys.argv) > 1 else 'map_output.png'
width = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
height = int(sys.argv[3]) if len(sys.argv) > 3 else 800

print(f"Erstelle Karte mit Größe {width}x{height}...")

# Karte erstellen (gleicher Code wie im Notebook)
center = [46.576157, 9.919649]
m = folium.Map(location=center, zoom_start=13, tiles=None)

# TileLayers hinzufügen
folium.TileLayer('OpenStreetMap', name='OpenStreetMap (Standard)').add_to(m)

folium.raster_layers.WmsTileLayer(
    url='https://wms.geo.admin.ch/',
    layers='ch.swisstopo.pixelkarte-farbe',
    fmt='image/png',
    name='Swisstopo',
    attr='&copy; <a href="https://www.swisstopo.admin.ch/">swisstopo</a>',
    overlay=False,
    control=True
).add_to(m)

# GPX-Verarbeitung
gpx_path = '250617_zuoz.gpx'
if os.path.exists(gpx_path):
    print(f"Lade GPX-Datei: {gpx_path}")
    with open(gpx_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    gpx_geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    for track in gpx.tracks:
        for segment in track.segments:
            coordinates = [[point.longitude, point.latitude] for point in segment.points]
            
            gpx_geojson['features'].append({
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': coordinates
                },
                'properties': {
                    'name': 'GPX Track Segment'
                }
            })

    geojson_layer = folium.GeoJson(
        gpx_geojson,
        name='Zuoz - Bever Kunstwanderung',
        style_function=lambda x: {
            'color': 'red',
            'weight': 3,
            'opacity': 0.7
        }
    ).add_to(m)
    
    m.fit_bounds(geojson_layer.get_bounds())
    print("GPX-Track zur Karte hinzugefügt")
else:
    print(f"Warnung: GPX-Datei '{gpx_path}' nicht gefunden")

folium.LayerControl().add_to(m)

# Als temporäre HTML-Datei speichern
tmpfile = 'temp_map_export.html'
print(f"Speichere temporäre HTML-Datei: {tmpfile}")
m.save(tmpfile)

# Screenshot mit Selenium erstellen
print("Erstelle Screenshot mit Chrome (headless)...")
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument(f'--window-size={width},{height}')

try:
    driver = webdriver.Chrome(options=options)
    driver.get(f'file://{os.path.abspath(tmpfile)}')
    time.sleep(3)  # Warten bis Karte vollständig geladen ist
    driver.save_screenshot(output_filename)
    driver.quit()
    print(f"✓ PNG erfolgreich erstellt: {output_filename}")
except Exception as e:
    print(f"✗ Fehler beim Erstellen des Screenshots: {e}")
    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    sys.exit(1)

# Aufräumen
if os.path.exists(tmpfile):
    os.remove(tmpfile)
    print("Temporäre HTML-Datei gelöscht")

print(f"\nFertig! Die Karte wurde als '{output_filename}' gespeichert.")
