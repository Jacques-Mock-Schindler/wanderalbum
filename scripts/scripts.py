"""
Utility functions for creating interactive maps and elevation profiles from GPX data.

This module provides functions to:
- Create interactive Folium maps with GPX track overlays
- Generate elevation profiles from GPX files
- Create Swisstopo URLs with embedded GPX tracks
- Generate QR codes for URLs
"""

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
    """
    Create an interactive Folium map with GPX track overlay and save as PNG.

    This function creates a Folium map centered at the specified coordinates,
    overlays a GPX track, and saves both an interactive HTML version and a
    PNG screenshot using Selenium. For PDF output formats, it displays an
    existing PNG file instead.

    Args:
        middle (list): Center coordinates as [latitude, longitude].
        path (str): Path to the GPX file to overlay on the map.
        title (str): Title for the GPX track layer.
        width (int, optional): Width of the output PNG in pixels. Defaults to 800.
        height (int, optional): Height of the output PNG in pixels. Defaults to 600.
        gpx_url (str, optional): URL to the GPX file (e.g., GitHub raw URL).
            If provided, prints the corresponding Swisstopo URL. Defaults to None.

    Returns:
        folium.Map: The created Folium map object.

    Raises:
        SystemExit: If screenshot creation fails.
    """
    is_pdf = os.environ.get('QUARTO_PROJECT_OUTPUT_FORMAT', '') == 'pdf'

    if gpx_url:
        print(f"Swisstopo URL: {create_swisstopo_url(middle, gpx_url)}")

    if is_pdf:
        display(Image(filename='map_output.png', width=800, height=600))
    else:
        import folium
        import gpxpy

    center = middle
    m = folium.Map(location=center,
                   zoom_start=13,
                   tiles=None)

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

    tempfile = 'temp_map_export.html'
    output_filename = 'map_output.png'
    m.save(tempfile)

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--window-size={width},{height}')

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(f'file://{os.path.abspath(tempfile)}')
        time.sleep(3)
        driver.save_screenshot(output_filename)
        driver.quit()
    except Exception as e:
        if os.path.exists(tempfile):
            os.remove(tempfile)
        sys.exit(1)

    if os.path.exists(tempfile):
        os.remove(tempfile)

    return m


def profile(path):
    """
    Generate and display an elevation profile from a GPX file.

    This function parses a GPX file, extracts elevation and distance data,
    creates a visualization with statistics, and saves it as a PNG file.
    The profile includes distance vs. elevation plot with min/max elevations,
    total ascent, and total descent information.

    Args:
        path (str): Path to the GPX file to process.

    Returns:
        None: The function saves 'elevation_profile.png' and displays the plot.
    """
    gpx_path = path

    if os.path.exists(gpx_path):
        with open(gpx_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

    distances = []
    elevations = []
    total_distance = 0

    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                if i == 0:
                    distances.append(0)
                else:
                    prev_point = segment.points[i - 1]
                    distance = point.distance_2d(prev_point)
                    total_distance += distance
                    distances.append(total_distance / 1000)
                elevations.append(point.elevation)

    plt.figure(figsize=(12, 4))
    plt.plot(distances, elevations, linewidth=2, color='#d62728')
    plt.fill_between(distances, elevations, alpha=0.3, color='#d62728')

    plt.xlabel('Distanz (km)', fontsize=12)
    plt.ylabel('Höhe (m ü. M.)', fontsize=12)
    plt.title('Höhenprofil', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)

    min_elevation = min(elevations)
    max_elevation = max(elevations)
    total_ascent = sum(elevations[i] - elevations[i - 1]
                       for i in range(1, len(elevations))
                       if elevations[i] > elevations[i - 1])
    total_descent = sum(elevations[i - 1] - elevations[i]
                        for i in range(1, len(elevations))
                        if elevations[i] < elevations[i - 1])

    plt.ylim(min_elevation - 200, max_elevation + 50)

    stats_text = (f'Distanz: {total_distance / 1000:.2f} km | '
                  f'Min: {min_elevation:.0f} m | Max: {max_elevation:.0f} m | '
                  f'↑ {total_ascent:.0f} m | ↓ {total_descent:.0f} m')
    plt.text(0.5, 0.02, stats_text, transform=plt.gca().transAxes,
             ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig('elevation_profile.png', dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()


def create_swisstopo_url(center, gpx_url):
    """
    Create a Swisstopo map URL with an embedded GPX track overlay.

    This function constructs a URL that opens the Swiss Federal Office of
    Topography (swisstopo) web map centered at the specified coordinates
    with a GPX track overlay from the provided URL.

    Args:
        center (list): Center coordinates as [latitude, longitude].
        gpx_url (str): URL to the GPX file (e.g., GitHub raw URL).

    Returns:
        str: The complete Swisstopo map URL with GPX overlay.
    """
    return ("https://map.geo.admin.ch/#/map?lang=de&center="
            + str(center[0]) + ","
            + str(center[1])
            + "&z=6&bgLayer=ch.swisstopo.pixelkarte-farbe&topic=ech&layers=GPX|"
            + gpx_url)


def generate_qr_code_for_url(url: str):
    """
    Generate a QR code for a URL and save it as a PNG image.

    This function creates a simple black-and-white QR code encoding the
    provided URL and saves it as 'qr_tag.png' in the current directory.

    Args:
        url (str): The URL to encode in the QR code.

    Returns:
        None: The function saves 'qr_tag.png' or prints an error message.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qr_tag.png")

    except Exception as e:
        print(f"❌ Ein Fehler ist aufgetreten: {e}")