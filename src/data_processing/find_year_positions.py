import ahocorasick
import xml.etree.ElementTree as ET
import json
from pathlib import Path
# Define the new path using pathlib
input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path

# Construct the full path to the JSON file
file_path = input_folder / 'year_patterns_no_punc.json'

# Open up JSON data of patterns
with open(file_path, 'r', encoding="utf-8") as file:
    year_data = json.load(file)

# create Automaton with patterns 
automaton = ahocorasick.Automaton()
for pattern in year_data:
    automaton.add_word(pattern.get("pattern"), (pattern.get("data"), pattern.get("pattern")))
automaton.make_automaton()
# Create an XML to store all references
new_root = ET.Element("Library")

# parse the raw file so we can match against the text

# Define the new path using pathlib
input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path

# Construct the full path to the XML file
file_path = input_folder / "25_his_wh_titles.xml"
history_tree = ET.parse(file_path)
history_root = history_tree.getroot()

# parse the emperor positions generated previously for Binary Search
# Define the new path using pathlib
input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path

# Construct the full path to the XML file
file_path = input_folder / "25_his_wh_titles_emp_pos.xml"
emperor_tree = ET.parse(file_path)
emperor_root = emperor_tree.getroot()

text_documents = history_root.findall(".//document")
match_documents = emperor_root.findall(".//document")

if len(text_documents) != len(match_documents):
    raise ValueError("The number of documents in both XMLs do not match!")

for text_doc, match_doc in zip(text_documents,match_documents):
    print("currently looking at: " + text_doc.get("eng_name")+ match_doc.get("eng_name"))
    # need to store the start and end leader in the emperor tree for binary search
    matches = match_doc.findall("emperor")

    # TODO needs to handle cases where there is maybe only 3 emperors mentioned ect
    start = 0
    end = len(matches) - 1
    print("length of matches currently examining " + str(len(matches)-1))
    # Text from Histories for searching
    document_text = text_doc.text

    new_document = ET.SubElement(new_root, "document")
    for key, value in text_doc.attrib.items():
        new_document.set(key, value)
    # now pattern match
    recent_pos = [-1,-1]
    for end_index, pattern in automaton.iter(document_text):
        # need to find appropriate position
        pos= (end_index - len(pattern[1]) + 1)
        if pos >= recent_pos[0] and pos <= recent_pos[1]:
            print("overlapping year")
            continue
        recent_pos = (pos,end_index)
        start_pos =int(matches[start].get("position"))
        end_pos = int(matches[end].get("position"))
        # case 1
        if pos < start_pos:
            ET.SubElement(new_document, "year", position = str(pos), name=pattern[1], value = str(pattern[0]-1 + int(matches[start].get("start"))))
        # case 2 
        elif pos > end_pos:
            ET.SubElement(new_document, "year", position = str(pos), name=pattern[1], value = str(pattern[0]-1 + int(matches[end].get("start"))))
        # case 3: Binary search to find appropriate position
        else:
            middle = (start+end) // 2
            middle_pos = int(matches[middle].get("position"))

            while(abs(start - end) != 1):
                if pos < middle_pos: 
                    end = middle
                    middle = (end + start) // 2
                    middle_pos = int(matches[middle].get("position"))
                    end_pos = int(matches[end].get("position"))
                elif pos > middle_pos:
                    start = middle
                    middle = (end + start) // 2
                    middle_pos = int(matches[middle].get("position"))
                    start_pos = int(matches[start].get("position"))
                else:
                    end = middle
                    break
            # TODO Does the start and end cross over? Need to verifty this
            ET.SubElement(new_document, "year", position = str(pos), name=pattern[1], value = str(pattern[0]-1 + int(matches[start].get("start"))))
        end = len(matches) - 1
        # print("new start: " + str(start))
        # print("new middle: " + str(middle))
        # print("new end: " + str(end))

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
document_name_and_path = output_dir / "25_his_wh_titles_no_punc_year_pos.xml"
new_tree.write(document_name_and_path, encoding="utf-8", xml_declaration=True)