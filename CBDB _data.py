import sqlite3

# Path to the extracted SQLite file
db_path = "cdbd_data/latest/latest.db"  # Replace with the actual path

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor to execute SQL queries
cursor = conn.cursor()

# Query to get the names of all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print the table names
print("Tables in the database:")
for table in tables:
    print(table[0])  # The table name is the first element of each tuple


# Example: Fetch the first 10 rows from a table
cursor.execute("SELECT c_personID, c_firstyear, c_lastyear, c_sequence, c_fy_range FROM STATUS_DATA WHERE c_status_code=47")  # Replace 'some_table' with an actual table name

# Get column names from the cursor description
column_names = [description[0] for description in cursor.description]

# Print the column names
print("Column names:")
for name in column_names:
    print(name, "|", end="")

rows = cursor.fetchall()
# Print the results
for row in rows:
    print(row)
# Replace 'some_table' with the name of the table you want to inspect
table_name = "STATUS_CODE_TYPE_REL"

# Use PRAGMA to get column information
cursor.execute(f"PRAGMA table_info({table_name});")
columns = cursor.fetchall()

# Print column details
print(f"Column information for table '{table_name}':")
print("cid | name | type | notnull | dflt_value | pk")
for column in columns:
    print(column)


# Print the results
for row in rows:
    print(row)
print("general exam data")
cursor.execute("SELECT c_personid, c_entry_code, c_year FROM ENTRY_DATA WHERE c_entry_code=36 AND c_year<200 AND c_year>100")
# Print the results
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()