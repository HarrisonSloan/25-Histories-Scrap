import xml.etree.ElementTree as ET
import os

# Created to 

def combine_and_flatten_xml(input_folder, output_file):
    # Create the root element of the combined XML
    combined_root = ET.Element("Library")

    # Loop through all XML files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".xml"):  # Only process XML files
            file_path = os.path.join(input_folder, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()
            print("Looking at a specific file now")
            # Find all 'document' elements
            for document in root.findall(".//document"):
                print("docuemnt name")
                print(document.get("eng_name"))
                # Create a new 'document' element in the combined XML
                new_document = ET.SubElement(combined_root, "document")
                # Copy over the attributes from the original document
                for key, value in document.attrib.items():
                    print(value)
                    new_document.set(key, value)
                # Concatenate all text from the 'volume' elements into one large string
                document_content = ""
                for volume in document.findall(".//volume"):
                    document_content += "\n"
                    document_content += volume.text or ""  # Add the text from each volume
                
                # Set the concatenated text as the content of the 'document'
                new_document.text = document_content.strip()  # Remove leading/trailing spaces

    # Write the combined XML to the output file
    tree = ET.ElementTree(combined_root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

# Example usage
combine_and_flatten_xml("raw_scrapped_by_volume", "25_Histories_raw.xml")