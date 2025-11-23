import json
import os

file_path = r'c:/Users/jcms/Documents/wanderalbum/files/2025/250617_oberengadin/oberengadin.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_source = [
    "import os\n",
    "import folium\n",
    "import gpxpy\n",
    "\n",
    "center = [46.576157, 9.919649]\n",
    "m = folium.Map(location=center,\n",
    "               zoom_start=13,\n",
    "               tiles=None\n",
    "               )\n",
    "\n",
    "folium.TileLayer('OpenStreetMap', name='OpenStreetMap (Standard)').add_to(m)\n",
    "\n",
    "folium.raster_layers.WmsTileLayer(\n",
    "    url='https://wms.geo.admin.ch/',\n",
    "    layers='ch.swisstopo.pixelkarte-farbe',\n",
    "    fmt='image/png',\n",
    "    name='Swisstopo',\n",
    "    attr='&copy; <a href=\"https://www.swisstopo.admin.ch/\">swisstopo</a>',\n",
    "    overlay=False,\n",
    "    control=True\n",
    ").add_to(m)\n",
    "\n",
    "# START: GPX-Verarbeitung\n",
    "gpx_path = '250617_zuoz.gpx'\n",
    "if os.path.exists(gpx_path):\n",
    "    with open(gpx_path, 'r') as gpx_file:\n",
    "        gpx = gpxpy.parse(gpx_file)\n",
    "\n",
    "    # GeoJSON-Feature erstellen\n",
    "    gpx_geojson = {\n",
    "        'type': 'FeatureCollection',\n",
    "        'features': []\n",
    "    }\n",
    "\n",
    "    for track in gpx.tracks:\n",
    "        for segment in track.segments:\n",
    "            # Extrahiere Koordinaten als [Länge, Breite] für GeoJSON\n",
    "            coordinates = [[point.longitude, point.latitude] for point in segment.points]\n",
    "            \n",
    "            gpx_geojson['features'].append({\n",
    "                'type': 'Feature',\n",
    "                'geometry': {\n",
    "                    'type': 'LineString',\n",
    "                    'coordinates': coordinates\n",
    "                },\n",
    "                'properties': {\n",
    "                    'name': 'GPX Track Segment'\n",
    "                }\n",
    "            })\n",
    "\n",
    "    # Füge GeoJSON zur Karte hinzu\n",
    "    geojson_layer = folium.GeoJson(\n",
    "        gpx_geojson,\n",
    "        name='Zuoz - Bever Kunstwanderung',\n",
    "        style_function=lambda x: {\n",
    "            'color': 'red',\n",
    "            'weight': 3,\n",
    "            'opacity': 0.7\n",
    "        }\n",
    "    ).add_to(m)\n",
    "    \n",
    "    m.fit_bounds(geojson_layer.get_bounds())\n",
    "\n",
    "# Fügen Sie das LayerControl-Element hinzu\n",
    "folium.LayerControl().add_to(m)\n",
    "m"
]

found = False
for cell in nb['cells']:
    if cell.get('id') == "d520e33c":
        cell['source'] = new_source
        found = True
        break

if found:
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Successfully modified notebook.")
else:
    print("Cell not found.")
