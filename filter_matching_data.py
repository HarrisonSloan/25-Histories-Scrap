import xml.etree.ElementTree as ET

# Load the input file
input_file = "25_Histories_unfiltered_matching_positions.xml"
output_file = "25_Histories_matching_positions.xml"

# Parse the XML file
tree = ET.parse(input_file)
root = tree.getroot()

# Iterate through each document
for document in root.findall("document"):
    matches = document.findall("match")
    updated_matches = []
    skip_until_type_1 = False
    current_type_3_value = "None"  # Ensure it's a string for consistency
    
    for i, match in enumerate(matches):
        match_type = int(match.attrib["type"])
        
        if match_type == 3:
            # Reset skip flag and set the current value of type 3
            skip_until_type_1 = True
            current_type_3_value = "None"  # Reset the value for this block
            updated_matches.append(match)
            
            # Look ahead for the next type 1 or type 3
            for j in range(i + 1, len(matches)):
                next_match_type = int(matches[j].attrib["type"])
                if next_match_type == 1:
                    current_type_3_value = matches[j].attrib["value"]
                    break
                elif next_match_type == 3:
                    break
            
            # Update the value of the current type 3 if it's "None"
            if match.attrib["value"] == "None":
                match.set("value", str(current_type_3_value))
        
        elif match_type == 2 and skip_until_type_1:
            # Skip type 2 matches until a type 1 is encountered
            continue
        
        elif match_type == 1:
            # Allow matches again after a type 1
            skip_until_type_1 = False
            updated_matches.append(match)
        
        else:
            # Add any other matches if not skipped
            updated_matches.append(match)
    
    # Clear the document matches and append the updated ones
    for match in matches:
        document.remove(match)
    for match in updated_matches:
        document.append(match)

# Save the modified XML to a new file
tree.write(output_file, encoding="utf-8", xml_declaration=True)

print(f"Processing complete. Output written to '{output_file}'.")
