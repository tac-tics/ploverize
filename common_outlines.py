# dictionaries/common.json
from collections import defaultdict
import sys
import json


# search_word = sys.argv[1]

with open('output/lapwing.json') as infile:
    lapwing_dictionary = json.load(infile)

lapwing_outlines_by_word = defaultdict(lambda: set())
for outline, word in lapwing_dictionary.items():
    lapwing_outlines_by_word[word].add(outline)


with open('output/main.json') as infile:
    main_dictionary = json.load(infile)

main_outlines_by_word = defaultdict(lambda: set())
for outline, word in main_dictionary.items():
    main_outlines_by_word[word].add(outline)


def suggest_for(search_word):
    main_outlines = main_outlines_by_word[search_word]
    lapwing_outlines = lapwing_outlines_by_word[search_word]
    return sorted(main_outlines & lapwing_outlines)


with open('output/main.words.json') as infile:
    MAIN_WORDS = set(json.load(infile))

dictionary = {}
for word in MAIN_WORDS:
    suggestions = suggest_for(word)
    if len(suggestions) == 1:
        outline = suggestions[0]
        dictionary[outline] = word

json.dump(dictionary, sys.stdout, indent=4)
