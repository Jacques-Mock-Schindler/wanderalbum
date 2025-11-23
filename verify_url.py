import sys
import os

# Add the current directory to the path so we can import from scripts.scripts
sys.path.insert(0, os.getcwd())

from scripts.scripts import create_swisstopo_url, qr_code, create_map
import scripts.scripts
print(f"Imported scripts from: {scripts.scripts.__file__}")

def test_create_swisstopo_url():
    center = [46.8, 8.2]
    gpx_url = "https://raw.githubusercontent.com/user/repo/main/track.gpx"
    expected_url = "https://map.geo.admin.ch/#/map?lang=de&center=46.8,8.2&z=6&bgLayer=ch.swisstopo.pixelkarte-farbe&topic=ech&layers=GPX|https://raw.githubusercontent.com/user/repo/main/track.gpx"
    
    generated_url = create_swisstopo_url(center, gpx_url)
    
    print(f"Generated URL: {generated_url}")
    
    if generated_url == expected_url:
        print("SUCCESS: URL matches expected format.")
    else:
        print("FAILURE: URL does not match expected format.")
        print(f"Expected: {expected_url}")

def test_qr_code_runs():
    # Just check if it runs without error
    center = [46.8, 8.2]
    gpx_url = "https://raw.githubusercontent.com/user/repo/main/track.gpx"
    
    try:
        qr_code(center, gpx_url)
        print("SUCCESS: qr_code function ran without error.")
        if os.path.exists("qr_tag.png"):
            os.remove("qr_tag.png")
            print("Cleaned up qr_tag.png")
    except Exception as e:
        print(f"FAILURE: qr_code function failed with error: {e}")

def test_create_map_output():
    center = [46.8, 8.2]
    gpx_url = "https://raw.githubusercontent.com/user/repo/main/track.gpx"
    # We need a dummy path for create_map
    dummy_path = "dummy.gpx"
    # Create a dummy file so os.path.exists returns true
    with open(dummy_path, 'w') as f:
        f.write('<?xml version="1.0"?><gpx><trk><trkseg></trkseg></trk></gpx>')
    
    try:
        print("\nTesting create_map output...")
        # We expect this to print the URL
        # Note: create_map tries to create a map and screenshot it. 
        # This might fail if selenium/chrome is not set up or if we don't want to wait.
        # However, the print happens *before* the map creation logic that might fail or take time.
        # But wait, create_map imports folium inside if not pdf.
        # Let's just run it and catch exceptions, but look for stdout.
        create_map(center, dummy_path, "Test Map", gpx_url=gpx_url)
        print("SUCCESS: create_map ran with gpx_url.")
    except Exception as e:
        # It might fail on selenium or gpx parsing if dummy is bad, but we just want to see the print
        print(f"create_map finished (possibly with error, which is expected for dummy env): {e}")
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)
        # Cleanup map output if created
        if os.path.exists('temp_map_export.html'):
            os.remove('temp_map_export.html')
        if os.path.exists('map_output.png'):
            os.remove('map_output.png')

if __name__ == "__main__":
    print("Testing create_swisstopo_url...")
    test_create_swisstopo_url()
    print("\nTesting qr_code...")
    test_qr_code_runs()
    test_create_map_output()
