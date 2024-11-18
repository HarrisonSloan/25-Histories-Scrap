import ahocorasick

automaton = ahocorasick.Automaton()

for idx, key in enumerate('年'.split()):
    automaton.add_word(key, (idx, key))

automaton.make_automaton()

with open("test_text.txt", "r", encoding="utf-8") as file:
    text = file.read()
    for end_index, pattern in automaton.iter(text):
        print(f"Found '{pattern}' at position {end_index - len(pattern) + 1}")