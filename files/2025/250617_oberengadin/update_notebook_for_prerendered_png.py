import json

# Read the notebook
with open('oberengadin.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find the cell with the map code
for cell in notebook['cells']:
    if cell['cell_type'] == 'code' and any('import os' in line and 'import folium' in ''.join(cell['source']) for line in cell['source']):
        # Update the source code to check for existing PNG first
        cell['source'] = [
            "import os\n",
            "import folium\n",
            "import gpxpy\n",
            "from IPython.display import Image, display\n",
            "\n",
            "# Prüfen, ob PDF-Format\n",
            "is_pdf = os.environ.get('QUARTO_PROJECT_OUTPUT_FORMAT', '') == 'pdf'\n",
            "\n",
            "# Wenn PDF-Format UND map_output.png existiert, verwende das vorhandene PNG\n",
            "if is_pdf and os.path.exists('map_output.png'):\n",
            "    display(Image(filename='map_output.png'))\n",
            "else:\n",
            "    # Sonst: Interaktive Karte erstellen\n",
            "    center = [46.576157, 9.919649]\n",
            "    m = folium.Map(location=center,\n",
            "                   zoom_start=13,\n",
            "                   tiles=None\n",
            "                   )\n",
            "    \n",
            "    folium.TileLayer('OpenStreetMap', name='OpenStreetMap (Standard)').add_to(m)\n",
            "    \n",
            "    folium.raster_layers.WmsTileLayer(\n",
            "        url='https://wms.geo.admin.ch/',\n",
            "        layers='ch.swisstopo.pixelkarte-farbe',\n",
            "        fmt='image/png',\n",
            "        name='Swisstopo',\n",
            "        attr='&copy; <a href=\"https://www.swisstopo.admin.ch/\">swisstopo</a>',\n",
            "        overlay=False,\n",
            "        control=True\n",
            "    ).add_to(m)\n",
            "    \n",
            "    # GPX-Verarbeitung\n",
            "    gpx_path = '250617_zuoz.gpx'\n",
            "    if os.path.exists(gpx_path):\n",
            "        with open(gpx_path, 'r') as gpx_file:\n",
            "            gpx = gpxpy.parse(gpx_file)\n",
            "    \n",
            "        gpx_geojson = {\n",
            "            'type': 'FeatureCollection',\n",
            "            'features': []\n",
            "        }\n",
            "    \n",
            "        for track in gpx.tracks:\n",
            "            for segment in track.segments:\n",
            "                coordinates = [[point.longitude, point.latitude] for point in segment.points]\n",
            "                \n",
            "                gpx_geojson['features'].append({\n",
            "                    'type': 'Feature',\n",
            "                    'geometry': {\n",
            "                        'type': 'LineString',\n",
            "                        'coordinates': coordinates\n",
            "                    },\n",
            "                    'properties': {\n",
            "                        'name': 'GPX Track Segment'\n",
            "                    }\n",
            "                })\n",
            "    \n",
            "        geojson_layer = folium.GeoJson(\n",
            "            gpx_geojson,\n",
            "            name='Zuoz - Bever Kunstwanderung',\n",
            "            style_function=lambda x: {\n",
            "                'color': 'red',\n",
            "                'weight': 3,\n",
            "                'opacity': 0.7\n",
            "            }\n",
            "        ).add_to(m)\n",
            "        \n",
            "        m.fit_bounds(geojson_layer.get_bounds())\n",
            "    \n",
            "    folium.LayerControl().add_to(m)\n",
            "    \n",
            "    # Für HTML: Interaktive Karte anzeigen\n",
            "    display(m)\n"
        ]
        break

# Write the updated notebook
with open('oberengadin.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print("Notebook updated successfully!")
print("\nWorkflow:")
print("1. Führen Sie 'python export_map_to_png.py' aus, um map_output.png zu erstellen")
print("2. Bei PDF-Rendering wird das vorhandene PNG verwendet")
print("3. Bei HTML-Rendering wird die interaktive Karte angezeigt")
