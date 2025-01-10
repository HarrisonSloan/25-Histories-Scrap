import ahocorasick
import xml.etree.ElementTree as ET
import json
from pathlib import Path
# Define the new path using pathlib
input_folder = Path(__file__).parent / "data/intermediate"  # Adjust the relative path

# # Construct the full path to the JSON file
# file_path = input_folder / 'year_patterns_no_punc.json'

# # Open up JSON data of patterns
# with open(file_path, 'r', encoding="utf-8") as file:
#     year_data = json.load(file)

# # create Automaton with patterns 
automaton = ahocorasick.Automaton()
# for pattern in year_data:
#     automaton.add_word(pattern.get("pattern"), (pattern.get("data"), pattern.get("pattern")))
automaton.add_word("十二年", (12, "十二年"))
automaton.add_word("十二", (2, "十二"))
automaton.make_automaton()



text = "xxx十二年二年"

recent_pos_and_length = [-1,0]
for end_index,pattern in automaton.iter(text):
    print(pattern)
    print("End index ", end_index)
    print("Len of the pattern ", len(pattern[1]))
    pos= (end_index - len(pattern[1]) + 1)
    print(pos)
    

    if  pos >= recent_pos_and_length[0] and pos <= recent_pos_and_length[1]:
        print("overlapping pattern")
    else:
        recent_pos_and_length[0]=pos
        recent_pos_and_length[1]=end_index
