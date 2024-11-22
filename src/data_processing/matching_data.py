import xml.etree.ElementTree as ET
import math
from pathlib import Path

input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path


# Create an XML to store all references
new_root = ET.Element("Library")

# parse volumnes
file_path = input_folder / "25_Histories_volume_positions.xml"
volume_tree = ET.parse(file_path)
volume_root = volume_tree.getroot()

# parse the emperor 
file_path = input_folder / "25_Histories_emperor_positions.xml"
emperor_tree = ET.parse(file_path)
emperor_root = emperor_tree.getroot()

# parse the years 
file_path = input_folder / "25_Histories_year_positions.xml"
year_tree = ET.parse(file_path)
year_root = year_tree.getroot()

volume_documents = volume_root.findall(".//document")
emperor_documents = emperor_root.findall(".//document")
year_documents = year_root.findall(".//document")

if len(volume_documents) != len(emperor_documents) != len(year_documents):
    raise ValueError("The number of documents in both XMLs do not match!")

for volume_doc, emperor_doc, year_doc in zip(volume_documents,emperor_documents,year_documents):
    # create document object for new XML
    print("currently looking at: " + year_doc.get("eng_name"))

    new_document = ET.SubElement(new_root, "document")
    for key, value in emperor_doc.attrib.items():
        new_document.set(key, value)

    # Volume positions in specific doc
    volume_matches = volume_doc.findall("end")
    current_vol_match = 0
    current_vol_match_pos = int(volume_matches[current_vol_match].get("position"))
    # Emperor positions in specific doc
    emperor_matches = emperor_doc.findall("emperor")
    current_emperor_match = 0
    current_emperor_match_pos = int(emperor_matches[current_emperor_match].get("position"))
    # Year positions in specific doc
    year_matches = year_doc.findall("year")
    current_year_match = 0
    current_year_match_pos = int(year_matches[current_year_match].get("position"))
    
    # Keep looping until we go over all matches for all 3 catergories
    while current_emperor_match != math.inf and current_year_match != math.inf and current_vol_match != math.inf:
        # emperor
        if min(current_vol_match_pos,current_emperor_match_pos,current_year_match_pos) == current_emperor_match_pos:
            # add emperor
            # make mid year
            if emperor_matches[current_emperor_match].get("end") != "None":
                val = (int(emperor_matches[current_emperor_match].get("start"))+int(emperor_matches[current_emperor_match].get("end"))) // 2
            else:
                val = int(emperor_matches[current_emperor_match].get("start"))
            name = emperor_matches[current_emperor_match].get("name")

            ET.SubElement(new_document,"match",type=str(1), value=str(val), name=name,position=str(current_emperor_match_pos))
            # Increment pointer
            current_emperor_match += 1
            # If beyond the end of the emperor matches
            if current_emperor_match > len(emperor_matches) - 1: 
                current_emperor_match = math.inf
            # Still within the emperor matches
            else: 
                current_emperor_match_pos = int(emperor_matches[current_emperor_match].get("position"))
        # year
        elif min(current_vol_match_pos,current_year_match_pos) == current_year_match_pos:
            val = year_matches[current_year_match].get("value")
            name = year_matches[current_year_match].get("name")
            ET.SubElement(new_document,"match",type=str(2), value=val, name=name,position=str(current_year_match_pos))
            current_year_match += 1
            if current_year_match > len(year_matches) - 1: 
                current_year_match = math.inf
            # Still within the emperor matches
            else: 
                current_year_match_pos = int(year_matches[current_year_match].get("position"))
            # add year
        # volume end
        else:

            # Special case that needs to be tracked TODO
            ET.SubElement(new_document,"match",type=str(3), value="None", name="end", position=str(current_vol_match_pos))
            current_vol_match += 1
            if current_vol_match > len(volume_matches) - 1: 
                current_vol_match = math.inf
            # Still within the emperor matches
            else: 
                current_vol_match_pos = int(volume_matches[current_vol_match].get("position"))


    continue

# Chat GBT function :)
# make the XML file readable
def prettify(element, level=0):
    indent = "  "  # Define your indent size
    i = "\n" + level * indent
    if len(element):
        if not element.text or not element.text.strip():
            element.text = i + indent
        if not element.tail or not element.tail.strip():
            element.tail = i
        for elem in element:
            prettify(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = i

# Create the XML file
new_tree = ET.ElementTree(new_root)
prettify(new_root)

# Define the directory and file name
output_dir = Path(__file__).parent / "../../data/intermediate"
output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

# Construct the full path
document_name_and_path = output_dir / "25_Histories_unfiltered_matching_positions_test.xml"
new_tree.write(document_name_and_path, encoding="utf-8", xml_declaration=True)