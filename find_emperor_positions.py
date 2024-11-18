import ahocorasick
import xml.etree.ElementTree as ET
import json

# Goal of this script is to produce a file detailing all the positions of the leaders based on JSON file detailing which leaders to search for
# Will use pattern matching library to achieve this and save the result in either a JSON or XML, which can be later used to produce the 
# number + year positions

automaton = ahocorasick.Automaton()


# Create a JSON or create an XML

new_root = ET.Element("Library")

# Open up JSON data
with open('emperors_year_1.json', 'r', encoding="utf-8") as file:
    emperor_data = json.load(file)
    

# Loop for each document to be made
# each document is just one of the 25 Histories
# create an automaton and patterns are just all of the leaders


tree = ET.parse("25_Histories_raw.xml")
root = tree.getroot()

for document in root.findall(".//document"):
    doc_name = document.get("eng_name")
    print("Looking at " + doc_name)
    # find all the emperors related to this specific doc
    for book in emperor_data.get("Books"):
        if book.get("name") == doc_name:
            print("Found")
            # create emperor automaton
            for emeperor in book.get("emperors"):
                print(emeperor.get("english_name"))
            
            # find every position 

            # append this to the new file we are makings
