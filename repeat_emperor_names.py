import json
from collections import defaultdict

# Load your JSON file
with open('emperors_year_1.json', 'r', encoding="utf-8") as file:
    data = json.load(file)

# Dictionary to store books with duplicate leader names
duplicate_leaders = {}

# Loop over each book
for book in data["Books"]:
    book_name = book['name']
    emperors = book['emperors']
    
    # Track occurrences of each leader's name in the current book
    name_count = defaultdict(int)
    for emperor in emperors:
        emperor_name = emperor['chinese_name']
        name_count[emperor_name] += 1
    
    # Find names with more than one occurrence
    duplicates_in_book = [name for name, count in name_count.items() if count > 1]
    
    # If duplicates found, add to result dictionary
    if duplicates_in_book:
        duplicate_leaders[book_name] = duplicates_in_book

# Print results
if duplicate_leaders:
    for book, leaders in duplicate_leaders.items():
        print(f"In book '{book}', the following leader names are duplicated: {leaders}")
else:
    print("No duplicate leader names found within any book.")