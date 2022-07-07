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



with open('data/words') as infile:
    WORDS = [line.strip() for line in infile.readlines()]


def count_words_starting_with(suffix):
    count = 0
    for word in WORDS:
        if word.startswith(suffix):
            count += 1

    return count


def count_words_ending_with(suffix):
    count = 0
    for word in WORDS:
        if word.endswith(suffix):
            count += 1

    return count


def main():
    allowable_chars = list(string.ascii_letters) + ["-", "'"]
    main_dict = load_dictionary('main')

    prefixes = []
    suffixes = []

    for outline, word in main_dict.items():
        if any(ch in outline for ch in string.digits):
            continue

        if '#' in outline:
            continue

        if word.startswith('{') and word.endswith('^}'):
            prefix = word[1:-2]
            if len(prefix) == 1:
                continue

            if all(ch in allowable_chars for ch in prefix):
                count = count_words_starting_with(prefix)
                prefixes.append((outline, prefix, count))

        elif word.startswith('{^') and word.endswith('}'):
            suffix = word[2:-1]
            if len(suffix) == 1:
                continue

            if all(ch in allowable_chars for ch in suffix):
                count = count_words_starting_with(suffix)
                suffixes.append((outline, suffix, count))


    with open('output/prefixes.txt', 'w') as outfile:
        for outline, prefix, count in sorted(prefixes, key=lambda tup: tup[2], reverse=True):
            print(outline.ljust(20), prefix.ljust(20), count, file=outfile)

    with open('output/suffixes.txt', 'w') as outfile:
        for outline, suffix, count in sorted(suffixes, key=lambda tup: tup[2], reverse=True):
            print(outline.ljust(20), suffix.ljust(20), count, file=outfile)


if __name__ == "__main__":
    main()

