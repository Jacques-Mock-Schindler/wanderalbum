import json

file_path = r'c:/Users/jcms/Documents/wanderalbum/files/2025/250617_oberengadin/oberengadin.ipynb'

with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

found = False
for cell in nb['cells']:
    if cell.get('id') == "0752542c":
        cell['source'] = [
            "![Auswanderer](auswanderer.jpg)\n",
            "\n",
            "In La Punt kann im Hotel Krone der Schlüssel für die meines Erachtens orginellste Installation abgeholt werden.\n",
            "\n",
            "Der Versuch, eines Oberengadiners, nach China auszuwandern."
        ]
        found = True
        break

if found:
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Successfully modified notebook.")
else:
    print("Cell not found.")
