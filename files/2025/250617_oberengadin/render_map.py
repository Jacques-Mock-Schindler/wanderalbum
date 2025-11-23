import folium
import gpxpy
import os

# Replicating the notebook code to generate the map

center = [46.576157, 9.919649]
m = folium.Map(location=center, zoom_start=13, tiles=None)

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

# START: GPX-Verarbeitung
gpx_path = '250617_zuoz.gpx'
if os.path.exists(gpx_path):
    with open(gpx_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # GeoJSON-Feature erstellen
    gpx_geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    for track in gpx.tracks:
        for segment in track.segments:
            # Extrahiere Koordinaten als [Länge, Breite] für GeoJSON
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

    # Füge GeoJSON zur Karte hinzu
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

# Fügen Sie das LayerControl-Element hinzu
folium.LayerControl().add_to(m)

# Save to HTML
m.save('map_for_screenshot.html')
print("Map saved to map_for_screenshot.html")
