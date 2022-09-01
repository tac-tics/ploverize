import re
import typing as t
from collections import defaultdict
import json


with open('output/final.json') as infile:
    dictionary = json.load(infile)


outlines_by_word = defaultdict(lambda: set())
for outline, word in dictionary.items():
    outlines_by_word[word].add(outline)


sentence = 'Getting information off the internet is like taking a drink from a fire hydrant.'

words = re.findall(r'(\b[^\s]+\b)', sentence)
for word in words:
    if word in outlines_by_word:
        outlines = outlines_by_word[word]
        outline = sorted(outlines)[0]
        print(word.ljust(20), outline)
