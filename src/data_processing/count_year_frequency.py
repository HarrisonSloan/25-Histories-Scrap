import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from pathlib import Path

# constants
shift = 140
# 140 for the 140 BCE 1912 for 1912 CE and 61 is the max year ahead you can get
arrLen = 140+1912+58

# Wide format
df = pd.DataFrame(
    {"year_freq": np.zeros(arrLen)}
)
# 

# Define the new path using pathlib
input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path

# Change to appropriate matching / year file
file_path = input_folder / "old_data.xml"
# might want to update this to accept only a year positions, emperor positions may be misleading...
emperor_tree = ET.parse(file_path)
emperor_root = emperor_tree.getroot()

#uncommnet if you want to use the matching data ... 
# for match_doc in emperor_root.findall(".//document"):
#     matches = match_doc.findall("match")
#     for match in matches:
#         # dont count "years" indicated by a start of volume 
#         if match.get("type") != "3":
#             df.iloc[shift+int(match.get("value")),0] += 1

#uncomment if you want to use the year data
for match_doc in emperor_root.findall(".//document"):
    matches = match_doc.findall("match")
    for match in matches:
        df.iloc[shift+int(match.get("value")),0] += 1

# Define the new path using pathlib
output_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path

# Construct the full path to save the CSV file
file_path = output_folder / "old_year_data.csv"

df.to_csv(file_path,index=False)