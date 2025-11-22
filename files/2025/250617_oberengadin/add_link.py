import json
import math

# WGS84 to LV95 conversion (approximate but sufficient for map link)
# Source: https://www.swisstopo.admin.ch/en/knowledge-facts/surveying-geodesy/reference-frames/transformations-position-scrambling.html
# Simplified for python without external libs if possible, or just use a simple formula.
# Actually, let's try to be accurate enough.

def wgs84_to_lv95(lat, lon):
    # Approximate conversion
    # phi = (lat * 3600 - 169028.66) / 10000
    # lam = (lon * 3600 - 26782.5) / 10000
    
    # Re-using standard formula for better accuracy if needed, but for a map link, 
    # we just need the center.
    # Let's use the official approximate formulas
    
    phi = (lat * 3600 - 169028.66) / 10000
    lam = (lon * 3600 - 26782.5) / 10000
    
    E = 2600072.37 + 211455.93 * lam - 10938.51 * lam * phi - 0.36 * lam * phi**2 - 44.54 * lam**3
    N = 1200147.07 + 308807.95 * phi + 3745.25 * lam**2 + 76.63 * phi**2 - 194.56 * lam**2 * phi + 119.79 * phi**3
    
    return E, N

lat = 46.576157
lon = 9.919649

E, N = wgs84_to_lv95(lat, lon)
print(f"Calculated LV95: E={E}, N={N}")

# Construct Link
# Zoom level mapping: Folium 13 is roughly Swisstopo 6 or 7. Let's try 6.
# Swisstopo zoom is different. 
# Let's use a standard zoom.
link = f"https://map.geo.admin.ch/?lang=de&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&E={E:.2f}&N={N:.2f}&zoom=6"

# Modify Notebook
file_path = r'c:/Users/jcms/Documents/wanderalbum/files/2025/250617_oberengadin/oberengadin.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the map cell (id: d520e33c) and insert a new markdown cell after it
map_cell_index = -1
for i, cell in enumerate(nb['cells']):
    if cell.get('id') == "d520e33c":
        map_cell_index = i
        break

if map_cell_index != -1:
    new_cell = {
        "cell_type": "markdown",
        "id": "swisstopo_link",
        "metadata": {},
        "source": [
            f"[öffnen auf swisstopo.ch]({link})"
        ]
    }
    # Check if the cell already exists to avoid duplicates if run multiple times
    if map_cell_index + 1 < len(nb['cells']) and nb['cells'][map_cell_index+1].get('id') == "swisstopo_link":
        nb['cells'][map_cell_index+1] = new_cell
        print("Updated existing link cell.")
    else:
        nb['cells'].insert(map_cell_index + 1, new_cell)
        print("Inserted new link cell.")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Successfully modified notebook.")
else:
    print("Map cell not found.")
