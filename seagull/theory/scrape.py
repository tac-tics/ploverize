from outline import is_valid_outline
import json


filenames = [
    "pronouns.md",
    "prepositions.md",
    "basic_verbs.md",
    "numbers.md",
    "contractions.md",
]


dictionary = {}


for filename in filenames:
    with open(filename) as infile:
        for line in infile:
            if line.startswith('- '):
                line = line[2:].strip()
                space_idx = line.index(' ')
                outline = line[:space_idx]
                word = line[space_idx + 1:]

                if outline == 'X':
                    print("Missing outline:", repr(word))
                else:
                    assert is_valid_outline(outline), f'invalid outline for {word!r}: {outline!r}'
                    dictionary[outline] = word

with open('dictionary.json', 'w') as outfile:
    json.dump(dictionary, outfile, indent=4)

