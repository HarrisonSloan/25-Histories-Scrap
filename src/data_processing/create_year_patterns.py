import json
from pathlib import Path
# All of the number+year combos
patterns = [("元年", 1),
            ("二年", 2),
            ("三年", 3),
            ("四年", 4),
            ("五年", 5),
            ("六年", 6),
            ("七年", 7),
            ("八年", 8),
            ("九年", 9),
            ("十年", 10),
            ("十一年", 11),
            ("十二年", 12),
            ("十三年", 13),
            ("十四年", 14),
            ("十五年", 15),
            ("十六年", 16),
            ("十七年", 17),
            ("十八年", 18),
            ("十九年", 19),
            ("二十年", 20),
            ("二十一年", 21),
            ("二十二年", 22),
            ("二十三年", 23),
            ("二十四年", 24),
            ("二十五年", 25),
            ("二十六年", 26),
            ("二十七年", 27),
            ("二十八年", 28),
            ("二十九年", 29),
            ("三十年", 30),
            ("三十一年", 31),
            ("三十二年", 32),
            ("三十三年", 33),
            ("三十四年", 34),
            ("三十五年", 35),
            ("三十六年", 36),
            ("三十七年", 37),
            ("三十八年", 38),
            ("三十九年", 39),
            ("四十年", 40),
            ("四十一年", 41),
            ("四十二年", 42),
            ("四十三年", 43),
            ("四十四年", 44),
            ("四十五年", 45),
            ("四十六年", 46),
            ("四十七年", 47),
            ("四十八年", 48),
            ("四十九年", 49),
            ("五十年", 50),
            ("五十一年", 51),
            ("五十二年", 52),
            ("五十三年", 53),
            ("五十四年", 54),
            ("五十五年", 55),
            ("五十六年", 56),
            ("五十七年", 57),
            ("五十八年", 58),
            ("五十九年", 59),
            ("六十年", 60),
            ("六十一年", 61),

]
# Define the set of punctuation symbols to prepend
punctuation_set = ["。", "，", "？", "：", "、", "⋯", "；", "）", "]", "！"]

# Build the JSON data structure
data = []
for pattern, value in patterns:
    for punctuation in punctuation_set:
        modified_pattern = punctuation + pattern
        data.append({
            "pattern": modified_pattern,
            "data": value  # Replace with actual data
        })


# Define the directory and ensure it exists
output_dir = Path(__file__).parent / "../../data/intermediate"
output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

# Construct the full path for the file
file_path = output_dir / "year_patterns_test.json"

# Save to a JSON file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4,ensure_ascii=False)