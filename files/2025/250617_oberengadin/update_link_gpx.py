import json

# Construct Link with GPX
# Raw GitHub URL for the GPX file
gpx_url = "https://raw.githubusercontent.com/Jacques-Mock-Schindler/wanderalbum/main/files/2025/250617_oberengadin/250617_zuoz.gpx"

# Coordinates (from previous step)
E = 2790156.34
N = 1161326.78
zoom = 6

# Swisstopo link with KML layer (pointing to GPX, Swisstopo often handles this via KML param or auto-detects)
# Documentation says layers=KML|url. Let's try that.
link = f"https://map.geo.admin.ch/?lang=de&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&E={E}&N={N}&zoom={zoom}&layers=KML|{gpx_url}"

# Modify Notebook
file_path = r'c:/Users/jcms/Documents/wanderalbum/files/2025/250617_oberengadin/oberengadin.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the link cell (id: swisstopo_link)
found = False
for cell in nb['cells']:
    if cell.get('id') == "swisstopo_link":
        cell['source'] = [
            f"[öffnen auf swisstopo.ch]({link})"
        ]
        found = True
        break

if found:
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Successfully updated link in notebook.")
else:
    print("Link cell not found.")
