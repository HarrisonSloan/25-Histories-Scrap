from collections import defaultdict
import xml.etree.ElementTree as ET
from pathlib import Path

input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust path
file_path = input_folder / "25_his_wh_titles_matching.xml"  # Your XML file

tree = ET.parse(file_path)
root = tree.getroot()

positions = defaultdict(set)

for document in root.findall('document'):
    eng_name = document.get('eng_name')
    for match in document.findall('match'):
        position = match.get('position')
        if position in positions[eng_name]:
            print(f"Duplicate found: eng_name={eng_name}, position={position}")
        else:
            positions[eng_name].add(position)