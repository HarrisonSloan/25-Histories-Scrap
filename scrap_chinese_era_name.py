import requests
from bs4 import BeautifulSoup
import json
import re


def extract_years(period):
    # Match start and end years with BCE/CE labels
    era = re.findall(r"BCE|CE", period)
    start_end = re.findall(r"\d+", period)
    if start_end:
        if len(start_end)==2:
            # Extract start and end year, along with BCE/CE
            start_year = int(start_end[0])
            end_year = int(start_end[1])
            if era:
                if era[0] == "BCE":
                    start_year = -start_year
                    end_year = -end_year
        elif len(start_end) == 1:
            start_year = int(start_end[0])
            end_year = None
            if era:
                if era[0] == "BCE":
                    start_year = -start_year
              
        return start_year, end_year
    else:
        # Return None if the format doesn't match
        return None, None

# URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_Chinese_era_names"

# Make a GET request to fetch the HTML content
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Define an empty list to store the data
emperors_data = []

# Find the table containing the list of Chinese era names
tables = soup.find_all("table", {"class": "wikitable"})
if not tables:
    print("No tables found with class 'wikitable'")

# Loop through each table (each dynasty section has its own table)
for table_index, table in enumerate(tables):
    print(f"Processing table {table_index + 1}")
    rows = table.find_all("tr")
    
    # Skip the header row
    for row_index, row in enumerate(rows[1:], start=2):
        cells = row.find_all("td")
        
        if len(cells) < 4:
            print(f"Row {row_index} skipped, not enough cells: {len(cells)}")
            continue  # Skip rows that don’t have enough data

        # Extract and clean text for each field
        names = cells[0].get_text(strip=True)
        period = cells[1].get_text(strip=True)
        
        # Extract English and Chinese name
        pattern = r"([A-Za-z\s]+)([\u4e00-\u9fff]+)"

# Apply the regex to match and separate English and Chinese parts
        match = re.match(pattern, names)

        if match:
            english_name = match.group(1).strip()  # First group captures the English name
            chinese_name = match.group(2).strip()


        # Extract start year from the period using regex
        start_year, end_year = extract_years(period)
        
        # # Print debug info for each emperor
        # print(f"Extracted data for row {row_index}:")
        # print(f" English Name: {english_name}")
        # print(f" Chinese Name: {chinese_name}")
        # print(f" Period: {period}")
        # print(f" Start Year: {start}")

        # Append each emperor's data as a dictionary
        emperor_data = {
            "english_name": english_name,
            "chinese_name": chinese_name,
            "start_year": start_year,
            "end_year": end_year
        }
        emperors_data.append(emperor_data)

# Check if data was collected
if not emperors_data:
    print("No emperor data collected. Please check the HTML structure and selectors.")
else:
    # Save the data to a JSON file
    with open("emperors_data.json", "w", encoding="utf-8") as f:
        json.dump({"emperors": emperors_data}, f, ensure_ascii=False, indent=4)
    print("Data saved to emperors_data.json")