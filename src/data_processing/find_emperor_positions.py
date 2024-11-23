import ahocorasick
import xml.etree.ElementTree as ET
import json
from pathlib import Path

# Create a JSON or create an XML
new_root = ET.Element("Library")

# Define the new path using pathlib
input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path

# Construct the full path to the JSON file
file_path = input_folder / 'emperors_year_1.json'
# Open up JSON data
with open(file_path, 'r', encoding="utf-8") as file:
    emperor_data = json.load(file)


# Define the new path using pathlib
input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path

# Construct the full path to the XML file
file_path = input_folder / "25_Histories_raw_excluded_his_jin_his_liao.xml"

# parse the raw file so we can match against the text
tree = ET.parse(file_path)
root = tree.getroot()

for document in root.findall(".//document"):
    # Get name of book to reference to find appropriate emperors list
    doc_name = document.get("eng_name")
    
    # Add document into 
    new_document = ET.SubElement(new_root, "document")
    for key, value in document.attrib.items():
        new_document.set(key, value)

    # find all the emperors related to this specific doc
    for book in emperor_data.get("Books"):
        # Found specific book in the JSON
        if book.get("name") == doc_name:
            
            # create emperor automaton for pattern matching
            automaton = ahocorasick.Automaton()
            i=0
            # Add every pattern (every emperor as specified by "emperors_year_1.json") -> later update to pass a file instead
            # ID is simply the start year as every one should have a different start year its also convient
            # as you can have this directly attached to the pattern itself
            # may need verification 
            for emperor in book.get("emperors"):
                key = emperor.get("chinese_name")
                automaton.add_word(key, ((emperor.get("start_year"),emperor.get("end_year")), key))
                i+=1
            automaton.make_automaton()

            # Get text from raw file
            document_text = document.text

            # Pattern match against the text for every specified pattern above
            # for every match create a new element in the XML 
            for end_index, pattern in automaton.iter(document_text):
                # there is no start date on the emperor
                if pattern[0][0] == None:
                    continue
                else:
                    ET.SubElement(new_document, "emperor", position=str(end_index - len(pattern) + 1), name=pattern[1], start=str(pattern[0][0]), end=str(pattern[0][1]))


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
document_name_and_path = output_dir / "25_Histories_emperor_positions_excluded_his_jin_his_liao.xml"

new_tree.write(document_name_and_path, encoding="utf-8", xml_declaration=True)