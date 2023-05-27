from collections import defaultdict 
import string
import os.path
import httpx
import json
import orthography
from copy import copy
import nltk


def load_main_dictionary():
    url = 'https://raw.githubusercontent.com/openstenoproject/plover/1e4d8b3bff0b705d936f14d31d5997456c5823cf/plover/assets/main.json'
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def save_dictionary(name, dictionary):
    filename = f'output/{name}.json'

    with open(filename, 'w') as outfile:
        json.dump(dictionary, outfile, indent=4, ensure_ascii=False)


def load_dictionary(name):
    filename = f'output/{name}.json'

    with open(filename) as infile:
        return json.load(infile)



dictionary = load_dictionary('008.main')

outlines_by_word = defaultdict(lambda: [])

for outline, word in dictionary.items():
    outlines_by_word[word].append(outline)


for word, outlines in sorted(outlines_by_word.items(), reverse=True, key=lambda pair: len(pair[1])):
    if len(outlines) > 1:
        print(word, len(outlines))
        for outline in outlines:
            print('   ', outline)
