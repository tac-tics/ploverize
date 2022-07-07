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


def main():
    allowable_chars = list(string.ascii_letters) + ["-", "'"]
    main_dict = load_dictionary('main')

    buckets = {}

    for outline, word in main_dict.items():
        strokes = outline.split('/')
        stroke_count = len(strokes)
        if stroke_count not in buckets:
            buckets[stroke_count] = []

        buckets[stroke_count].append(outline)

    with open('output/stroke_count.txt', 'w') as outfile:
        for stroke_count, outlines in sorted(buckets.items(), key=lambda pair: pair[0]):
            print(len(outlines), 'have', stroke_count, 'strokes', file=outfile)


if __name__ == "__main__":
    main()
