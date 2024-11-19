import ahocorasick
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# set this for Chinese font in plots
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

# constants
shift = 140
# 140 for the 140 BCE 1912 for 1912 CE and 61 is the max year ahead you can get
arrLen = 140+1912+61

# Tongpan, Buzheng, Ancha
patterns = ["通判","布政","按察"]

# create automaton for pattern matching
automaton = ahocorasick.Automaton()
# i is used to reference each pattern
i=0
for pattern in patterns:
    automaton.add_word(pattern, (i, pattern))
    i+=1
automaton.make_automaton()

# create data frame
df = pd.DataFrame({
    "Pattern": patterns,
    "Data": [np.zeros(arrLen) for _ in patterns]  # Creates an array of zeros for each pattern
})
# Long format ->
# The long format organizes data so that each element of every array corresponds to one row. For example:
# If you have 10 patterns and each array has 100 elements, this results in 10×100=1000 rows.
# This approach is more suitable for element-wise operations, but if your primary operations focus on aligning by row (index) across patterns, the wide format is a better fit. 
df2 = pd.DataFrame({
    "Pattern": np.repeat(patterns, arrLen),
    "Index": np.tile(np.arange(arrLen), len(patterns)),
    "Value": np.zeros(len(patterns) * arrLen)
})

# Wide format
df3 = pd.DataFrame(
    {pattern: np.zeros(arrLen) for pattern in patterns}
)

print(df)
print(df2)
print(df3)

# parse the raw file so we can match against the text
history_tree = ET.parse("25_Histories_raw.xml")
history_root = history_tree.getroot()

# parse the year positions generated previously for Binary Search
emperor_tree = ET.parse("25_Histories_year_positions.xml")
emperor_root = emperor_tree.getroot()
# parse the main text
text_documents = history_root.findall(".//document")
match_documents = emperor_root.findall(".//document")

if len(text_documents) != len(match_documents):
    raise ValueError("The number of documents in both XMLs do not match!")

for text_doc, match_doc in zip(text_documents,match_documents):
    matches = match_doc.findall("match")
    # TODO needs to handle cases where there is maybe only 3 emperors mentioned ect, currently not needed but probably safe to add this
    start = 0
    middle = len(matches) // 2
    end = len(matches) - 1
    # Text from Histories for searching
    document_text = text_doc.text

    # now pattern match
    for end_index, pattern in automaton.iter(document_text):
        # need to find appropriate position
        pos= (end_index - len(pattern) + 1)
        start_pos =int(matches[start].get("position"))
        middle_pos = int(matches[middle].get("position"))
        end_pos = int(matches[end].get("position"))
        # case 1
        if pos < start_pos:
            # For specific pattern increment data
            df.at[pattern[0],"Data"][shift+int(matches[start].get("value"))] += 1
            df3.iloc[shift+int(matches[start].get("value")),pattern[0]] += 1
        # case 2 
        elif pos > end_pos:
            # For specific pattern increment data
            df.at[pattern[0],"Data"][shift+int(matches[end].get("value"))] += 1
            df3.iloc[shift+int(matches[end].get("value")),pattern[0]] += 1
            continue
        # case 3: Binary search to find appropriate position
        else:
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
            df.at[pattern[0],"Data"][shift+int(matches[start].get("value"))] += 1
            df3.iloc[shift+int(matches[start].get("value")),pattern[0]] += 1
        # reset end, start doesnt need to be reset as patterns are forward search found (the position of the next occurrence only increases)
        end = len(matches) - 1


# Access data and plot
for _, row in df.iterrows():
    plt.plot(row["Data"], label=row["Pattern"])

# Add legend and labels
plt.legend()
plt.xlabel("Index")
plt.ylabel("Value")
plt.title("Pattern Data Arrays")

# Shift the y-axis labels by a specific amount (for example, shifting by +5 units)
ticks = plt.gca().get_xticks()  # Get current y-ticks
plt.gca().set_xticklabels([tick - 140 for tick in ticks])  # Shift labels by 5

# Show the plot
plt.legend()
plt.show()