import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# constants
shift = 140
# 140 for the 140 BCE 1912 for 1912 CE and 61 is the max year ahead you can get
arrLen = 140+1912+58

# Wide format
df = pd.DataFrame(
    {"year_freq": np.zeros(arrLen)}
)
print(df)
# 
emperor_tree = ET.parse("25_Histories_matching_positions.xml")
emperor_root = emperor_tree.getroot()

for match_doc in emperor_root.findall(".//document"):
    matches = match_doc.findall("match")
    for match in matches:
        if match.get("value") != "None":
            df.iloc[shift+int(match.get("value")),0] += 1
print(df)
df.to_csv("year_1_frequency.csv",index=False)