import ahocorasick
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
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

# # create data frame
# df = pd.DataFrame({
#     "Pattern": patterns,
#     "Data": [np.zeros(arrLen) for _ in patterns]  # Creates an array of zeros for each pattern
# })
# # Long format ->
# # The long format organizes data so that each element of every array corresponds to one row. For example:
# # If you have 10 patterns and each array has 100 elements, this results in 10×100=1000 rows.
# # This approach is more suitable for element-wise operations, but if your primary operations focus on aligning by row (index) across patterns, the wide format is a better fit. 
# df2 = pd.DataFrame({
#     "Pattern": np.repeat(patterns, arrLen),
#     "Index": np.tile(np.arange(arrLen), len(patterns)),
#     "Value": np.zeros(len(patterns) * arrLen)
# })

# Wide format
df3 = pd.DataFrame(
    {pattern: np.zeros(arrLen) for pattern in patterns}
)

# print(df)
# print(df2)
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
            #df.at[pattern[0],"Data"][shift+int(matches[start].get("value"))] += 1
            df3.iloc[shift+int(matches[start].get("value")),pattern[0]] += 1
        # case 2 
        elif pos > end_pos:
            # For specific pattern increment data
            #df.at[pattern[0],"Data"][shift+int(matches[end].get("value"))] += 1
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
            #df.at[pattern[0],"Data"][shift+int(matches[start].get("value"))] += 1
            df3.iloc[shift+int(matches[start].get("value")),pattern[0]] += 1
        # reset end, start doesnt need to be reset as patterns are forward search found (the position of the next occurrence only increases)
        end = len(matches) - 1



# GRAPHING AND DATA SECTION


# Read in year frequency for normalisation purposes
year_df = pd.read_csv("year_1_frequency.csv")

# Create a final all data to save to CSV

# Create normalised data
year_freq = year_df["year_freq"]
df_normalised = df3.div(year_freq,axis=0)
df_normalised = df_normalised.fillna(0)

# add year column
df3["year"] = np.arange(-140,len(df3)+1-141)
df_normalised["year"] = np.arange(-140,len(df3)+1-141)

# Plot all patterns against the "Year" column
plt.figure(figsize=(12, 6))  # Adjust the figure size for better visibility
for column in df3.columns[:-1]:  # Exclude the "Year" column
    plt.plot(df3["year"], df3[column], label=column)

# Add labels, title, and legend
plt.xlabel('Year')
plt.ylabel('Value')
plt.title('Patterns Over Time')
plt.legend(title="Patterns", loc="upper left")
plt.grid(True)  # Optional: Add grid for better readability
plt.show()



# Plot all patterns against the "Year" column
plt.figure(figsize=(12, 6))  # Adjust the figure size for better visibility
for column in df_normalised.columns[:-1]:  # Exclude the "Year" column
    plt.plot(df_normalised["year"], df_normalised[column], label=column)

# Add labels, title, and legend
plt.xlabel('Year')
plt.ylabel('Normalized Value')
plt.title('Normalized Patterns Over Time')
plt.legend(title="Patterns", loc="upper left")
plt.grid(True)  # Optional: Add grid for better readability
plt.show()

# Function to bin data and calculate year ranges
def bin_and_add_year_ranges_with_year(df, bin_size=10):
    binned_data = []
    year_ranges = []  # List to store year range strings

    # Extract the Year column
    years = df["year"]

    # Drop the "Year" column from the DataFrame to process other columns
    data_without_year = df.drop(columns=["year"])

    # Loop through the DataFrame in steps of `bin_size`
    for i in range(0, len(df), bin_size):
        # Get the current chunk (bin)
        chunk = data_without_year.iloc[i:i + bin_size]

        # Sum the chunk rows and append to binned data
        binned_data.append(chunk.sum())

        # Calculate the year range for the current bin using the Year column
        start_year = years.iloc[i]
        end_year = years.iloc[min(i + bin_size - 1, len(years) - 1)]
        year_range = f"{start_year}-{end_year}"
        year_ranges.append(year_range)

    # Create a new DataFrame from the binned data
    binned_df = pd.DataFrame(binned_data, columns=data_without_year.columns)

    # Add the "Year_Range" column to the binned DataFrame
    binned_df["Year_Range"] = year_ranges

    return binned_df

# Create the binned DataFrame with year ranges
df_binned_with_ranges = bin_and_add_year_ranges_with_year(df3, bin_size=10)
print(df_binned_with_ranges)

# step = 5  # Show every 2nd label

# plt.figure(figsize=(12, 6))
# plt.bar(df_binned_with_ranges["Year_Range"], df_binned_with_ranges[patterns[0]], label=patterns[0])

# # Adjust x-axis ticks
# plt.xticks(ticks=range(0, len(df_binned_with_ranges), step), 
#            labels=df_binned_with_ranges["Year_Range"][::step], 
#            rotation=45)

# # Add labels and title
# plt.xlabel('Year Range')
# plt.ylabel('Binned Value')
# plt.title('Binned Data Over Year Ranges')
# plt.legend()
# plt.grid(True)
# plt.show()

# second option to adjust number of labels
plt.figure(figsize=(12, 6))
plt.bar(df_binned_with_ranges["Year_Range"], df_binned_with_ranges[patterns[0]], label=patterns[0])

# Automatically limit the number of x-axis labels
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=50))  # Adjust nbins as needed

# Add labels and title
plt.xlabel('Year Range')
plt.ylabel('Binned Value')
plt.title('Binned Data Over Year Ranges')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()


# Plot all patterns with Year_Range on the x-axis
plt.figure(figsize=(12, 6))

# Iterate over each pattern column, excluding the "Year_Range" column
for column in df_binned_with_ranges.columns[:-1]:  # Exclude the "Year_Range" column
    plt.plot(df_binned_with_ranges["Year_Range"], df_binned_with_ranges[column], label=column)

# Automatically limit the number of x-axis labels
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=50))  # Adjust nbins for fewer/more labels

# Add labels, title, and legend
plt.xlabel('Year Range')
plt.ylabel('Binned Value')
plt.title('Binned Patterns Over Year Ranges')
plt.xticks(rotation=45)  # Rotate x-axis labels for readability
plt.legend(title="Patterns", loc="upper left")
plt.grid(True)

# Show the plot
plt.show()




# Save data to CSV
# save normalised and normal data first
final_df = pd.concat([df3,year_df,df_normalised],axis=1)
final_df.to_csv("Final_data.csv",index=False)

# save binned data
df_binned_with_ranges.to_csv("Final_bin.csv",index=False)