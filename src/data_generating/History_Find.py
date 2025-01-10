import ahocorasick
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from matplotlib.ticker import MaxNLocator
from pathlib import Path

# constants
shift = 140
# 140 for the 140 BCE 1912 for 1912 CE and 61 is the max year ahead you can get
arrLen = 140+1912+58

# Tongpan, Buzheng, Ancha follwed by 3 other random positions
#patterns = ["通判","布政","按察"]
patterns = ["通判","布政","按察","通侯","課第售","川師", "專知", "司員", "殿前神威軍"]
# patterns = ["布政"]
#patterns = ["通判"]
def history_find(patterns, histories_file, year_data_file):
    """
    Function that patterns matches against the pattern and finds the closest associated year via year_data_file. Returns a frequency count for each pattern for 
    years 140 BC to 1973 BC
    """
    input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path
    # create automaton for pattern matching
    automaton = ahocorasick.Automaton()
    # i is used to reference each pattern
    i=0
    for pattern in patterns:
        automaton.add_word(pattern, (i, pattern))
        i+=1
    automaton.make_automaton()

    # Data frame to store a frequency counter for each pattern from year 140 BC to 1973
    pattern_occurences_df = pd.DataFrame(
        {pattern: np.zeros(arrLen) for pattern in patterns}
    )

    # parse the raw file so we can match against the text
    file_path = input_folder / histories_file
    history_tree = ET.parse(file_path)
    history_root = history_tree.getroot()

    # parse the match positions generated previously for Binary Search
    file_path = input_folder / year_data_file
    match_tree = ET.parse(file_path)
    match_root = match_tree.getroot()
    # parse the main text
    text_documents = history_root.findall(".//document")
    match_documents = match_root.findall(".//document")

    if len(text_documents) != len(match_documents):
        raise ValueError("The number of documents in both XMLs do not match!")
    overall_matches = 0
    miss_matches = 0
    match_types = [0,0,0]
    for text_doc, match_doc in zip(text_documents,match_documents):
        matches = match_doc.findall("match")
        # TODO needs to handle cases where there is maybe only 3 emperors mentioned ect, currently not needed but probably safe to add this
        
        # These refer to the matches contained in the year_data_file. 
        # So start = 0 is just the first match object, where as start_pos is the value of the match object
        start = 0
        end = len(matches) - 1

        # Text from Histories for searching
        document_text = text_doc.text
        print(text_doc.get("eng_name"))
    
        # now pattern match on a particular document in the Histories (1 of the 25 Historical documents)
        for end_index, pattern in automaton.iter(document_text):
            overall_matches+=1
            # need to find appropriate position
            pos= (end_index - len(pattern[1]) + 1)
            start_pos =int(matches[start].get("position"))
            end_pos = int(matches[end].get("position"))

            # case 1: position of match is before any mention of number+year
            if pos < start_pos:
                # For specific pattern (a column) increment data of found year
                pattern_occurences_df.iloc[shift+int(matches[start].get("value")),pattern[0]] += 1
                match_types[int(matches[start].get("type")) - 1] +=1
            # case 2: position of match is after any mention of number+year
            elif pos > end_pos:
                # For specific pattern (a column) increment data of found year
                pattern_occurences_df.iloc[shift+int(matches[end].get("value")),pattern[0]] += 1
                match_types[int(matches[end].get("type")) - 1] +=1
                continue
            
            # case 3: position of match is between mentions of number+year 
            # Binary search on the year mentions to find closest year mention to site of match
            else:
                # get the middle match and its value
                middle = (end + start) // 2 
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
                
                # If a match doesnt occur between a volume where there is no mention of an emperor ignore the data 
                if matches[start].get("value") != "None":
                    pattern_occurences_df.iloc[shift+int(matches[start].get("value")),pattern[0]] += 1
                    match_types[int(matches[start].get("type")) - 1] +=1
                else:
                    miss_matches+=1
            # reset end, start doesnt need to be reset as patterns are forward search found (the position of the next occurrence only increases)
            end = len(matches) - 1

    return overall_matches, miss_matches, match_types, pattern_occurences_df

matches, miss_matches, match_types, main_data = history_find(patterns,"25_his_wh_titles.xml","25_his_wh_titles_matching.xml")
# main_data["year"] = np.arange(-140,len(main_data)+1-141)
output_folder = Path(__file__).parent / "../../data/final"  # Adjust the relative path
file_path = output_folder / "patterns_intial.csv"
main_data.to_csv(file_path,encoding="utf-8", index=False)
print(matches)
print(miss_matches)
print(match_types)