import ahocorasick
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import sqlite3
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

# constants
shift = 140
# 140 for the 140 BCE 1912 for 1912 CE and 61 is the max year ahead you can get
arrLen = 140+1912+58

def append_pattern_match(conn, pattern, pattern_pos, year, book, match_position, type_):
    """
    Appends a pattern match to the pattern_matches table.
    
    Args:
        conn: SQLite connection object.
        pattern: The pattern string.
        pattern_pos: The position of the pattern in the text.
        year: The associated year value.
        book: The name of the book (document_name).
        match_position: The position in the book for the match.
        type_: The type of match.
        
    Returns:
        True if the insertion was successful, False otherwise.
    """
    try:
        cursor = conn.cursor()

        # Retrieve match ID from the matches table
        cursor.execute('''
        SELECT id FROM matches
        WHERE eng_name = ? AND position = ?
        ''', (book, match_position))
        result = cursor.fetchone()

        # Check if a match was found
        if result is None:
            print(f"No match found for book: {book}, position: {match_position}")
            return False

        match_id = result[0]  # Extract the ID from the result tuple

        # Insert into pattern_matches table
        cursor.execute('''
        INSERT INTO pattern_matches (pattern, pattern_position, year, book, match_id, type)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (pattern, pattern_pos, year, book, match_id, type_))
        
        conn.commit()  # Commit the transaction
        return True

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False



def history_find(conn, patterns, histories_file, year_data_file):
    """
    Function that patterns matches against the pattern and finds the closest associated year via year_data_file. Returns a frequency count for each pattern for 
    years 140 BC to 1973 BC
    """

    # Create the database
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pattern_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern TEXT,
        year INTEGER,
        pattern_position INTEGER,
        book TEXT,
        match_id INTEGER, 
        type INTEGER
    )
    ''')
    conn.commit()


    input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path
    # create automaton for pattern matching
    automaton = ahocorasick.Automaton()
    # i is used to reference each pattern
    i=0
    for pattern in patterns:
        automaton.add_word(pattern, (i, pattern))
        i+=1
    automaton.make_automaton()

    # Data frame to store frequency for each pattern, but divide the matches in respective types
    initial_data = {pattern: [[0, 0, 0] for _ in range(arrLen)] for pattern in patterns}
    pattern_occurences_df = pd.DataFrame(initial_data)

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
        book_name = text_doc.get("eng_name")
        document_text = text_doc.text

    
        # now pattern match on a particular document in the Histories (1 of the 25 Historical documents)
        for end_index, pattern in automaton.iter(document_text):
            overall_matches+=1
            # need to find appropriate position
            pos= (end_index - len(pattern)[1] + 1)
            start_pos =int(matches[start].get("position"))
            end_pos = int(matches[end].get("position"))

            # case 1: position of match is before any mention of number+year
            if pos < start_pos:
                # For specific pattern (a column) increment data of found year
                year = int(matches[start].get("value"))
                type = int(matches[start].get("type")) - 1
                pattern_occurences_df.iloc[shift+year,pattern[0]][type] += 1
                append_pattern_match(conn,pattern[1],pos,year,book_name,start_pos,type)
                match_types[int(matches[start].get("type")) - 1] +=1
            # case 2: position of match is after any mention of number+year
            elif pos > end_pos:
                year = int(matches[start].get("value"))
                type = int(matches[start].get("type")) - 1
                # For specific pattern (a column) increment data of found year
                pattern_occurences_df.iloc[shift+year,pattern[0]][type] += 1
                append_pattern_match(conn,pattern[1],pos,year,book_name,end_pos,type)

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
                    year = int(matches[start].get("value"))
                    type = int(matches[start].get("type")) - 1
                    pattern_occurences_df.iloc[shift+year,pattern[0]][type] += 1
                    append_pattern_match(conn,pattern[1],pos,year,book_name,start_pos,type)
                    match_types[int(matches[start].get("type")) - 1] +=1
                else:
                    miss_matches+=1
            # reset end, start doesnt need to be reset as patterns are forward search found (the position of the next occurrence only increases)
            end = len(matches) - 1

    return overall_matches, miss_matches, match_types, pattern_occurences_df

def parse_xml_to_db(conn, xml_file):
    """
    This is taking the matching XML table and putting this in a database. This is so you can reference what pattern/loc to a certain entry in this XML/table
    """
    input_folder = Path(__file__).parent / "../../data/intermediate"  # Adjust the relative path
    file_path = input_folder / xml_file
    tree = ET.parse(file_path)
    root = tree.getroot()
    cursor = conn.cursor()
    
    for document in root.findall('document'):
        eng_name = document.get('eng_name')
        
        for match in document.findall('match'):
            match_type = match.get('type')
            value = match.get('value')
            name = match.get('name')
            position = match.get('position')
            
            # Insert into the database
            cursor.execute('''
            INSERT INTO matches (eng_name, type, value, name, position)
            VALUES (?, ?, ?, ?, ?)
            ''', (eng_name, match_type, value, name, position))
    
    conn.commit()

if __name__=="__main__":
    
    # Update these 
    matching_data_file = "25_his_wh_titles_matching.xml"
    text_file = "25_his_wh_titles.xml"
    
    # create the database
    # Connect to SQLite database
    # Alter name if you want to maintain multiple
    conn = sqlite3.connect('matches.db')
    cursor = conn.cursor()

    # Create the matches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eng_name TEXT,
        type INTEGER,
        value TEXT,
        name TEXT,
        position INTEGER
    )
    ''')
    cursor.execute('''CREATE UNIQUE INDEX unique_book_position ON matches (eng_name, position)''')
    conn.commit()
    parse_xml_to_db(conn, matching_data_file)

    # Tongpan, Buzheng, Ancha follwed by 3 other random positions
    #patterns = ["通判","布政","按察"]
    patterns = ["通判","布政","按察","通侯","課第售","川師", "專知", "司員", "殿前神威軍"]
    # patterns = ["布政"]
    #patterns = ["通判"]

    matches, miss_matches, match_types, main_data = history_find(conn, patterns,text_file,matching_data_file)
    
    # Save the time series to a CSV
    output_folder = Path(__file__).parent / "../../data/final"  # Adjust the relative path
    file_path = output_folder / "patterns_intial_additional_data.csv"
    main_data.to_csv(file_path,encoding="utf-8", index=False)
    # Show basic information
    print(matches)
    print(miss_matches)
    print(match_types)






# for pattern in patterns: 
#     # Extract the data for the chosen pattern
#     values = main_data[pattern].tolist()

#     # Create time series for each of the three values
#     time_series = list(zip(*values))  # Transpose the list of lists
#     time = range(len(values))  # Create time points

#     # Plot each series
#     plt.figure(figsize=(8, 5))
#     for i, series in enumerate(time_series):
#         plt.plot(time, series, label=f"Value {i + 1}")

#     plt.title(f"Time Series for {pattern}")
#     plt.xlabel("Time")
#     plt.ylabel("Values")
#     plt.legend()
#     plt.grid()
#     plt.show()