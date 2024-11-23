import ahocorasick
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from matplotlib.ticker import MaxNLocator
from pathlib import Path
# set this for Chinese font in plots
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

# constants
shift = 140
# 140 for the 140 BCE 1912 for 1912 CE and 61 is the max year ahead you can get
arrLen = 140+1912+58

# Tongpan, Buzheng, Ancha follwed by 3 other random positions
patterns = ["通判","布政","按察"]
#patterns = ["通判","布政","按察","通侯","課第售","川師", "專知", "司員", "殿前神威軍"]
# patterns = ["布政"]

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
    patter_occurences_df = pd.DataFrame(
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
    for text_doc, match_doc in zip(text_documents,match_documents):
        matches = match_doc.findall("match")
        # TODO needs to handle cases where there is maybe only 3 emperors mentioned ect, currently not needed but probably safe to add this
        
        # These refer to the matches contained in the year_data_file. 
        # So start = 0 is just the first match object, where as start_pos is the value of the match object
        start = 0
        end = len(matches) - 1

        # Text from Histories for searching
        document_text = text_doc.text

    
        # now pattern match on a particular document in the Histories (1 of the 25 Historical documents)
        for end_index, pattern in automaton.iter(document_text):
            overall_matches+=1
            # need to find appropriate position
            pos= (end_index - len(pattern) + 1)
            start_pos =int(matches[start].get("position"))
            end_pos = int(matches[end].get("position"))

            # case 1: position of match is before any mention of number+year
            if pos < start_pos:
                # For specific pattern (a column) increment data of found year
                patter_occurences_df.iloc[shift+int(matches[start].get("value")),pattern[0]] += 1
            
            # case 2: position of match is after any mention of number+year
            elif pos > end_pos:
                # For specific pattern (a column) increment data of found year
                patter_occurences_df.iloc[shift+int(matches[end].get("value")),pattern[0]] += 1
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
                    patter_occurences_df.iloc[shift+int(matches[start].get("value")),pattern[0]] += 1
                else:
                    miss_matches+=1
            # reset end, start doesnt need to be reset as patterns are forward search found (the position of the next occurrence only increases)
            end = len(matches) - 1
    return overall_matches, miss_matches, patter_occurences_df

matches, miss_matches, main_data = history_find(patterns,"25_Histories_raw_excluded_his_jin_his_liao.xml","25_Histories_matching_positions_excluded_his_jin_his_liao.xml")
print(matches)
print(miss_matches)
# # GRAPHING AND DATA SECTION
# print(matches)
# print(main_data)

# Read in year frequency for normalisation purposes
input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path
file_path = input_folder / "year_1_frequency_excluded_his_jin_his_liao.csv"
year_freq_df = pd.read_csv(file_path)
year_freq_df["year"] = np.arange(-140,len(main_data)+1-141)

def process_data(main_data, year_freq, bin_size=10):
    # Step 1: Aggregate every 3 consecutive columns
    # Group columns in sets of 3
    aggregated_data = []
    column_names = []
    for i in range(0, len(main_data.columns), 3):
        # Sum the data in groups of 3
        agg_group = main_data.iloc[:, i:i+3].sum(axis=1).copy()  # Make a copy to avoid view issues
        aggregated_data.append(agg_group)
        
        # Create column name by joining the original pattern names
        new_col_name = ",".join(main_data.columns[i:i+3])
        column_names.append(new_col_name)
    
    # Create the DataFrame with aggregated data
    aggregated_df = pd.DataFrame(aggregated_data).T
    aggregated_df.columns = column_names
    
    # Step 2: Bin the data by 10-year intervals
    # We assume `year_freq` has a 'Year' column
    binned_data = []
    binned_year_freq = []
    year_ranges = []
    
    for i in range(0, len(aggregated_df), bin_size):
        # Get the chunk of data for the bin
        chunk = aggregated_df.iloc[i:i + bin_size].copy()  # Make a copy to avoid view issues
        year_chunk = year_freq.iloc[i:i + bin_size].copy()  # Make a copy of the year_freq chunk
        
        # Sum the data for each column in the bin
        binned_chunk = chunk.sum().copy()  # Make sure we're working with a copy
        binned_year_freq_chunk = year_chunk["year_freq"].sum()
        
        # Create the year range for this bin
        start_year = year_chunk["year"].iloc[0]
        end_year = year_chunk["year"].iloc[-1]
        year_ranges.append(f"{start_year}-{end_year}")
        
        binned_data.append(binned_chunk)
        binned_year_freq.append(binned_year_freq_chunk)
    
    # Convert the binned data into a DataFrame
    binned_df = pd.DataFrame(binned_data)
    binned_df["year_Range"] = year_ranges
    
    # Normalize the binned data by dividing by binned year frequency
    for col in binned_df.columns.difference(["year_Range"]):
        # Replace zero in year_freq with zero for normalization to avoid division by zero
        binned_df[col] = binned_df[col] / np.where(binned_year_freq != 0, binned_year_freq, 1)  # Safe division
        binned_df[col] = binned_df[col].fillna(0)  # Replace NaN values with 0
        binned_df[col] = binned_df[col].replace(np.inf, 0)  # Replace infinity values with 0
        
    return binned_df

def plot_processed_data(processed_data):
    # Set the figure size
    plt.figure(figsize=(12, 6))
    
    # Plot each column (excluding "Year_Range") against the Year_Range
    for col in processed_data.columns.difference(['year_Range']):
        plt.plot(processed_data['year_Range'], processed_data[col], label=col)
    # Automatically limit the number of x-axis labels
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=50))  # Adjust nbins as needed
    # Add labels and title
    plt.xlabel('Year Range')
    plt.ylabel('Normalized Value')
    plt.title('Normalized Binned Data Over Time (excluded_his_jin_his_liao)')
    
    # Rotate x-axis labels for better visibility
    plt.xticks(rotation=45)
    
    # Add a legend
    plt.legend(title="Patterns", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Display the plot
    plt.tight_layout()
    plt.show()




processed_data = process_data(main_data, year_freq_df)

# Example usage:
plot_processed_data(processed_data)

# Define the new path using pathlib
output_folder = Path(__file__).parent / "../../data/final"  # Adjust the relative path

# Construct the full path to save the CSV file
file_path = output_folder / "history_find_raw_out_excluded_his_jin_his_liao.csv"
processed_data.to_csv(file_path,encoding="utf-8")

