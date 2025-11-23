# scripts.py

import folium
import gpxpy
import os
from IPython.display import Image, display
import matplotlib.pyplot as plt
import qrcode
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_map(middle, path, title, width=800, height=600, gpx_url=None):
    # middle ist eine Liste mit [lat, lng]
    # path ist der Pfad zur GPX-Datei
    # Prüfen, ob PDF-Format
    is_pdf = os.environ.get('QUARTO_PROJECT_OUTPUT_FORMAT', '') == 'pdf'

    if gpx_url:
        print(f"Swisstopo URL: {create_swisstopo_url(middle, gpx_url)}")

    if is_pdf:
        # Für PDF: Verwende das vorhandene PNG
        display(Image(filename='map_output.png' , width=800, height=600 ))
    else:
        # Für HTML: Interaktive Folium-Karte erstellen
        import folium
        import gpxpy
    
    center = middle
    m = folium.Map(location=center,
                   zoom_start=13,
                   tiles=None
                   )
    
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
    gpx_path = path
    if os.path.exists(gpx_path):
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
            name=title,
            style_function=lambda x: {
                'color': 'red',
                'weight': 3,
                'opacity': 0.7
            }
        ).add_to(m)
        
        m.fit_bounds(geojson_layer.get_bounds())
    
    folium.LayerControl().add_to(m)

    # Als temporäre HTML-Datei speichern
    tempfile = 'temp_map_export.html'
    output_filename = 'map_output.png'
    # print(f"Speichere temporäre HTML-Datei: {tempfile}")
    m.save(tempfile)

    # Screenshot mit Selenium erstellen
    # print("Erstelle Screenshot mit Chrome (headless)...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--window-size={width},{height}')

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(f'file://{os.path.abspath(tempfile)}')
        time.sleep(3)  # Warten bis Karte vollständig geladen ist
        driver.save_screenshot(output_filename)
        driver.quit()
        # print(f"✓ PNG erfolgreich erstellt: {output_filename}")
    except Exception as e:
        # print(f"✗ Fehler beim Erstellen des Screenshots: {e}")
        if os.path.exists(tempfile):
            os.remove(tempfile)
        sys.exit(1)

    # Aufräumen
    if os.path.exists(tempfile):
        os.remove(tempfile)
        # print("Temporäre HTML-Datei gelöscht")

    # print(f"\\nFertig! Die Karte wurde als '{output_filename}' gespeichert.")

    return m

def profile(path):
    # GPX-Datei laden
    gpx_path = path

    if os.path.exists(gpx_path):
        with open(gpx_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
    
    # Daten extrahieren
    distances = []
    elevations = []
    total_distance = 0
    
    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                if i == 0:
                    distances.append(0)
                else:
                    prev_point = segment.points[i-1]
                    distance = point.distance_2d(prev_point)
                    total_distance += distance
                    distances.append(total_distance / 1000)
                elevations.append(point.elevation)
    
    # Höhenprofil erstellen
    plt.figure(figsize=(12, 4))
    plt.plot(distances, elevations, linewidth=2, color='#d62728')
    plt.fill_between(distances, elevations, alpha=0.3, color='#d62728')
    
    plt.xlabel('Distanz (km)', fontsize=12)
    plt.ylabel('Höhe (m ü. M.)', fontsize=12)
    plt.title('Höhenprofil', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
# scripts.py

import folium
import gpxpy
import os
from IPython.display import Image, display
import matplotlib.pyplot as plt
import qrcode
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_map(middle, path, title, width=800, height=600):
    # middle ist eine Liste mit [lat, lng]
    # path ist der Pfad zur GPX-Datei
    # Prüfen, ob PDF-Format
    is_pdf = os.environ.get('QUARTO_PROJECT_OUTPUT_FORMAT', '') == 'pdf'

    if is_pdf:
        # Für PDF: Verwende das vorhandene PNG
        display(Image(filename='map_output.png' , width=800, height=600 ))
    else:
        # Für HTML: Interaktive Folium-Karte erstellen
        import folium
        import gpxpy
    
    center = middle
    m = folium.Map(location=center,
                   zoom_start=13,
                   tiles=None
                   )
    
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
    gpx_path = path
    if os.path.exists(gpx_path):
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
            name=title,
            style_function=lambda x: {
                'color': 'red',
                'weight': 3,
                'opacity': 0.7
            }
        ).add_to(m)
        
        m.fit_bounds(geojson_layer.get_bounds())
    
    folium.LayerControl().add_to(m)

    # Als temporäre HTML-Datei speichern
    tempfile = 'temp_map_export.html'
    output_filename = 'map_output.png'
    # print(f"Speichere temporäre HTML-Datei: {tempfile}")
    m.save(tempfile)

    # Screenshot mit Selenium erstellen
    # print("Erstelle Screenshot mit Chrome (headless)...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--window-size={width},{height}')

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(f'file://{os.path.abspath(tempfile)}')
        time.sleep(3)  # Warten bis Karte vollständig geladen ist
        driver.save_screenshot(output_filename)
        driver.quit()
        # print(f"✓ PNG erfolgreich erstellt: {output_filename}")
    except Exception as e:
        # print(f"✗ Fehler beim Erstellen des Screenshots: {e}")
        if os.path.exists(tempfile):
            os.remove(tempfile)
        sys.exit(1)

    # Aufräumen
    if os.path.exists(tempfile):
        os.remove(tempfile)
        # print("Temporäre HTML-Datei gelöscht")

    # print(f"\\nFertig! Die Karte wurde als '{output_filename}' gespeichert.")

    return m

def profile(path):
    # GPX-Datei laden
    gpx_path = path

    if os.path.exists(gpx_path):
        with open(gpx_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
    
    # Daten extrahieren
    distances = []
    elevations = []
    total_distance = 0
    
    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                if i == 0:
                    distances.append(0)
                else:
                    prev_point = segment.points[i-1]
                    distance = point.distance_2d(prev_point)
                    total_distance += distance
                    distances.append(total_distance / 1000)
                elevations.append(point.elevation)
    
    # Höhenprofil erstellen
    plt.figure(figsize=(12, 4))
    plt.plot(distances, elevations, linewidth=2, color='#d62728')
    plt.fill_between(distances, elevations, alpha=0.3, color='#d62728')
    
    plt.xlabel('Distanz (km)', fontsize=12)
    plt.ylabel('Höhe (m ü. M.)', fontsize=12)
    plt.title('Höhenprofil', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Statistiken
    min_elevation = min(elevations)
    max_elevation = max(elevations)
    total_ascent = sum(elevations[i] - elevations[i-1] for i in range(1, len(elevations)) if elevations[i] > elevations[i-1])
    total_descent = sum(elevations[i-1] - elevations[i] for i in range(1, len(elevations)) if elevations[i] < elevations[i-1])
    
    # Y-Achse anpassen: 200m unter dem tiefsten Punkt
    plt.ylim(min_elevation - 200, max_elevation + 50)
    
    stats_text = f'Distanz: {total_distance/1000:.2f} km | Min: {min_elevation:.0f} m | Max: {max_elevation:.0f} m | ↑ {total_ascent:.0f} m | ↓ {total_descent:.0f} m'
    plt.text(0.5, 0.02, stats_text, transform=plt.gca().transAxes,
             ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('elevation_profile.png', dpi=150, bbox_inches='tight')
    plt.close()

def create_swisstopo_url(center, gpx_url):
    """
    Erstellt eine Swisstopo-URL mit eingeblendetem GPX-Track.
    
    Args:
        center: Liste oder Tupel mit [lat, lng] Koordinaten
        gpx_url: URL zur GPX-Datei (z.B. GitHub Raw URL)
        
    Returns:
        str: Die vollständige URL zur Swisstopo-Karte
    """
    return ("https://map.geo.admin.ch/#/map?lang=de&center=" 
            + str(center[0]) + "," 
            + str(center[1]) 
            + "&z=6&bgLayer=ch.swisstopo.pixelkarte-farbe&topic=ech&layers=GPX|" 
            + gpx_url)

def generate_qr_code_for_url(url: str):
    """
    Generiert einen simplen (schwarz-weiß) QR-Code für eine URL
    und speichert ihn als Bilddatei (PNG).

    Args:
        url (str): Die URL, die im QR-Code codiert werden soll.
        filename (str): Der Name der Ausgabedatei (z.B. 'qr_code.png').
    """
    try:
        # 1. QR-Code-Generator-Objekt erstellen
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L, # Fehlerkorrektur
            box_size=10, # Größe der einzelnen Pixel
            border=4,    # Größe des weißen Rands
        )

        # 2. Daten (URL) hinzufügen und Code generieren lassen
        qr.add_data(url)
        qr.make(fit=True)

        # 3. Das schlichte QR-Code-Bild erstellen (Standard-Methode)
        # fill_color: Farbe der Quadrate (z.B. Schwarz)
        # back_color: Farbe des Hintergrunds (z.B. Weiß)
        img = qr.make_image(fill_color="black", back_color="white")

        # 4. Bild speichern
        img.save("qr_tag.png")
        

    except Exception as e:
        print(f"❌ Ein Fehler ist aufgetreten: {e}")
    