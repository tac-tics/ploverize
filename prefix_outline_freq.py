from collections import defaultdict
import string
import os.path
import httpx
import json
from copy import copy


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


main_dictionary = load_dictionary('005.main')
affix_dict = load_dictionary('affix_dictionary')

first_strokes = defaultdict(lambda: 0)

for outline in main_dictionary:
    strokes = outline.split('/')
    first_stroke = strokes[0]
    if first_stroke in affix_dict:
        first_strokes[first_stroke] += 1


for stroke, count in sorted(first_strokes.items(), reverse=True, key=lambda pair: pair[1]):
    print(stroke.ljust(10), count)

