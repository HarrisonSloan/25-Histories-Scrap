import sqlite3
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from pathlib import Path
# set this for Chinese font in plots
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

# constants
shift = 140
# 140 for the 140 BCE 1912 for 1912 CE and 61 is the max year ahead you can get
arrLen = 140+1912+61


def save_ouput_csv(fileName,rows):
    with open(fileName, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        column_names = [desc[0] for desc in cursor.description]
        writer.writerow(column_names)

        # Write the data rows
        for row in rows:
            writer.writerow(row)
    return

# Define the new path using pathlib
db_folder = Path(__file__).parent / "../../data/raw"  # Adjust the relative path

# Construct the full path to the SQLite database file
db_path = db_folder / "cdbd_data/latest/latest.db"

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor to execute SQL queries
cursor = conn.cursor()

# Query explanation
# Find all entry data for anyone of the entry_code 36
# (36, 'examination: jinshi (general)', '科舉: 進士(籠統)')
# Add the c_index_year of the individual and order by c_year
query = """
SELECT
    ENTRY_DATA.c_personid, c_year, c_index_year 
FROM 
    ENTRY_DATA
    JOIN BIOG_MAIN
    ON BIOG_MAIN.c_personid = ENTRY_DATA.c_personid
WHERE 
    c_entry_code=36 AND c_index_year IS NOT NULL AND c_index_year>0
ORDER BY
    c_index_year
"""

cursor.execute(query)
rows = cursor.fetchall()
# Path to the output CSV file
save_ouput_csv("historical_exam_data.csv",rows)  # You can change the file name/path as needed



query = """
SELECT 
    c_index_year
FROM 
    BIOG_MAIN
WHERE
    c_index_year IS NOT NULL AND c_index_year < 2000
ORDER BY
    c_index_year
"""


cursor.execute(query)
rows = cursor.fetchall()
# for row in rows:
#     print(row)
save_ouput_csv("historical_people_data.csv",rows)



# read exam data
exam_df = pd.read_csv("historical_exam_data.csv")
# read in person data
people_df = pd.read_csv("historical_people_data.csv")

year_exam_counter = [0]*arrLen
year_people_counter = [0]*arrLen

for year in exam_df['c_index_year']:
    year_exam_counter[year+shift] += 1

for year in people_df['c_index_year']:
    year_people_counter[year+shift] += 1

normalized_data = [
    count / norm if norm != 0 else 0
    for count, norm in zip(year_exam_counter, year_people_counter)
]

# Step 3: Create a DataFrame
df = pd.DataFrame({
    'Year': np.arange(-140,len(year_exam_counter)+1-141),
    'Original Count': year_exam_counter,
    'Normalization Count': year_people_counter,
    'Normalized Data': normalized_data
})

# Step 4: Save the DataFrame to a CSV
# Define the new path using pathlib
output_folder = Path(__file__).parent / "../../data/final"  # Adjust the relative path

# Construct the full path to save the CSV file
file_path = output_folder / "CBDB_normalized_data.csv"

df.to_csv(file_path, index=False)
print(f"Data saved to {file_path}")

# Step 5: Plot the normalized data
plt.figure(figsize=(10, 6))
plt.plot(df['Year'], df['Normalized Data'], color='orange', linewidth=2, label='Normalized Data')

# Add labels, title, and legend
plt.xlabel('Year')
plt.ylabel('Normalized Frequency')
plt.title('Normalized Frequency of Years')
plt.legend()
plt.grid(True)  # Optional grid for better readability

# Display the plot
plt.show()