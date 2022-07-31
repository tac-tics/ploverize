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


LEFTS = "STKPWHR"
RIGHTS = "FRPBLGTSDZ"
MIDDLES = "AO*EU"


def split_stroke(stroke):
    mode = 'left'

    left = []
    middle = []
    right = []

    for ch in stroke:
        if mode == 'left':
            if ch == '-':
                mode = 'right'
            elif ch in MIDDLES:
                mode = 'middle'
            else:
                left.append(ch)

        if mode == 'middle':
            if ch not in MIDDLES:
                mode = 'right'
            else:
                middle.append(ch)

        if mode == 'right':
            right.append(ch)

    if len(middle) == 0 and len(right) > 0:
        # trim leading '-'
        right = right[1:]

    return ''.join(left), ''.join(middle), ''.join(right)


def is_valid_side(side, reference):
    filtered_reference = ''
    for ch in reference:
        if ch in side:
            filtered_reference += ch

    return side == filtered_reference



assert is_valid_side('SKR', LEFTS)
assert is_valid_side('', LEFTS)
assert is_valid_side(LEFTS, LEFTS)
assert not is_valid_side('SRK', LEFTS)
assert not is_valid_side('SRA', LEFTS)
assert not is_valid_side('#', LEFTS)
assert not is_valid_side('s', LEFTS)
assert not is_valid_side('0', LEFTS)


def is_valid_stroke(stroke):
    left, middle, right = split_stroke(stroke)
    return (
        is_valid_side(left, LEFTS) and
        is_valid_side(middle, MIDDLES) and
        is_valid_side(right, RIGHTS)
    )


assert is_valid_stroke('SRA')
assert is_valid_stroke('-Z')


def is_valid_outline(outline):
    strokes = outline.split('/')
    return all(is_valid_stroke(stroke) for stroke in strokes)


def filter_valid_outlines(dictionary):
    valid_outlines_dict = {}
    for outline, word in dictionary.items():
        if is_valid_outline(outline):
            valid_outlines_dict[outline] = word
    return valid_outlines_dict


def split_dictionary(dictionary, predicate):
    true_dict = {}
    false_dict = {}

    for outline, word in dictionary.items():
        if predicate(word):
            true_dict[outline] = word
        else:
            false_dict[outline] = word

    return true_dict, false_dict


def is_affix(word):
    return word.startswith('{^') or word.endswith('^}') or word.startswith('{&') or word.endswith('&}')

def has_punctuation(word):
    return any(ch in word for ch in '.,?/:;[]^&%$#@!()')


def is_multiword(word):
    return ' ' in word


def is_proper_noun(word):
    return word != word.lower() and word != 'I'


def main():
    dictionary = load_main_dictionary()
    save_dictionary('main', dictionary)

    dictionary = filter_valid_outlines(dictionary)
    save_dictionary('001.main', dictionary)

    affix_dictionary, dictionary = split_dictionary(dictionary, is_affix)
    save_dictionary('002.main', dictionary)
    save_dictionary('affix_dictionary', affix_dictionary)

    proper_dictionary, dictionary = split_dictionary(dictionary, is_proper_noun)
    save_dictionary('003.main', dictionary)
    save_dictionary('proper_dictionary', proper_dictionary)

    punctuation_dictionary, dictionary = split_dictionary(dictionary, has_punctuation)
    save_dictionary('004.main', dictionary)
    save_dictionary('punctuation_dictionary', punctuation_dictionary)

    multiword_dictionary, dictionary = split_dictionary(dictionary, is_multiword)
    save_dictionary('005.main', dictionary)
    save_dictionary('multiword_dictionary', multiword_dictionary)


if __name__ == "__main__":
    main()
