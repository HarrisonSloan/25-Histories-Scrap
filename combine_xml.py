import xml.etree.ElementTree as ET
import os

# Created to combine all the raw scrapped data

def combine_and_flatten_xml(input_folder, text_output_file, vol_pos_output_file):
    # Create the root element of the combined XML
    combined_root = ET.Element("Library")
    vol_pos_root = ET.Element("Library")
    # Loop through all XML files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".xml"):  # Only process XML files
            file_path = os.path.join(input_folder, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()
            print("Looking at a specific file now")
            # Find all 'document' elements
            for document in root.findall(".//document"):
                print("document name")
                print(document.get("eng_name"))
                # Create a new 'document' element in the combined XML
                new_document = ET.SubElement(combined_root, "document")
                new_document_vol_pos = ET.SubElement(vol_pos_root, "document")
                # Copy over the attributes from the original document
                for key, value in document.attrib.items():
                    print(value)
                    new_document.set(key, value)
                    new_document_vol_pos.set(key, value)
                # Concatenate all text from the 'volume' elements into one large string
                document_content = ""
                i=0
                for volume in document.findall(".//volume"):
                    document_content += "\n"
                    document_content += volume.text or ""  # Add the text from each volume
                    ET.SubElement(new_document_vol_pos,"end",id=str(i),position=str(len(document_content)))
                    i+=1
                
                # Set the concatenated text as the content of the 'document'
                new_document.text = document_content.strip()  # Remove leading/trailing spaces

    # Write the combined XML to the output file
    tree_text = ET.ElementTree(combined_root)
    prettify(combined_root)
    tree_text.write(text_output_file, encoding="utf-8", xml_declaration=True)
    # Write the volume position to an XML file 
    tree_vol_pos = ET.ElementTree(vol_pos_root)
    prettify(vol_pos_root)
    tree_vol_pos.write(vol_pos_output_file, encoding="utf-8", xml_declaration=True)

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

# Example usage
combine_and_flatten_xml("raw_scrapped_by_volume", "25_Histories_raw.xml","volume_positions.xml")