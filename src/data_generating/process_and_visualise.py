
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from matplotlib.ticker import MaxNLocator
from pathlib import Path
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']


# frequency data

# pattern data
input_folder = Path(__file__).parent / "../../data/final"  # Adjust the relative path
file_path = input_folder / "patterns_intial_inc_matching.csv"
main_data = pd.read_csv(file_path)

# Read in year frequency for normalisation purposes
input_folder = Path(__file__).parent / "../../data/intermediate" 
# Adjust relative to pick appropriate frequency file
file_path = input_folder / "year_1_frequency_exc_his_jin_his_liao_no_title_no_punc_matching.csv"
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


processed_data = process_data(main_data, year_freq_df,10)

# Example usage:
plot_processed_data(processed_data)

# Define the new path using pathlib
output_folder = Path(__file__).parent / "../../data/final"  # Adjust the relative path

# Construct the full path to save the CSV file
file_path = output_folder / "pattern_binned_10_inc_matching.csv"
processed_data.to_csv(file_path,encoding="utf-8")
# file_path = output_folder / "history_find_raw_all_patterns_excluded_his_jin_his_liao.csv"
# main_data.to_csv(file_path,encoding="utf-8")
