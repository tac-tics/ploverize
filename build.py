from collections import defaultdict
import string
import os.path
import httpx
import json
import orthography
from copy import copy
import nltk
import shutil


def load_net_dictionary(url):
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def load_main_dictionary():
    url = 'https://raw.githubusercontent.com/openstenoproject/plover/1e4d8b3bff0b705d936f14d31d5997456c5823cf/plover/assets/main.json'
    return load_net_dictionary(url)


def save_dictionary(name, dictionary):
    filename = f'output/{name}.json'

    with open(filename, 'w') as outfile:
        json.dump(dictionary, outfile, indent=4, ensure_ascii=False)


def load_dictionary(name):
    filename = f'output/{name}.json'

    with open(filename) as infile:
        return json.load(infile)


CMUDICT = nltk.corpus.cmudict.dict()


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


def filter_briefs(dictionary):
    new_dictionary = copy(dictionary)

    with open('dictionaries/briefs.json') as infile:
        briefs_dictionary = json.load(infile)

    for brief_word in briefs_dictionary.values():
        for outline, word in dictionary.items():
            if word == brief_word and outline in new_dictionary:
                del new_dictionary[outline]

    return new_dictionary


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


def filter_common_prefixes(dictionary):
    new_dictionary = copy(dictionary)

    prefixes = {
        'A': 'a',
        'EUPB': 'in',
        'RE': 're',
        'EBGS': 'ex',
        'TKE': 'de',
        'AOE': 'e',
        'RAOE': 're',
        'TKEUS': 'dis',
        'UPB': 'un',
        'EPB': 'en',
        'EUPL': 'im',
        'KAUPB': 'con',
        'PRO': 'pro',
        'PRE': 'pre',
        'EUPBT': 'inter',
        'EPL': 'em',
        'EUR': 'ir',
        'KA': 'ka',
        'AB': 'ab',
        'SE': 'se',
    }

    for outline, word in dictionary.items():
        first_stroke = outline.split('/')[0]
        base_outline = '/'.join(outline.split('/')[1:])

        if base_outline not in dictionary:
            continue

        base_word = dictionary[base_outline]
        prefix = prefixes.get(first_stroke)

        if prefix and orthography.combine(prefix, base_word) == word:
            #print('deleting', outline, word, '=', prefix, "+", base_word)
            del new_dictionary[outline]

    return new_dictionary


def filter_common_suffixes(dictionary):
    new_dictionary = copy(dictionary)

    suffixes = {
        '-G': 'ing',
        '-D': 'ed',
        '-S': 's',
        '-Z': 's',
        'EU': 'y',
        'HR': 'l',
        'ER': 'er',
        'EUBG': 'ic',
        'HREU': 'ly',
        'ER': 'er',
        'TEU': 'ty',
        '*ER': 'er',
#        'KWRA': 'a',
        'KWREU': 'y',
        '-BL': 'ble',
        'REU': 'ly',
        'ERS': 'ers',
        '*PBS': 'iness',
        'SEU': 'cy',
        'EUS': 'is',
        'A*L': 'al',
        'KHREU': 'ically',
        'T*EUF': 'tive',
        'EUF': 'ive',
        'K-L': 'cal',
        'KWRAL': 'ial',
        '*EUPB': 'in',
        '*L': "le",
        'PWHREU': 'bly',
        'HRAR': 'lar',
        '-LS': 'less',
        'TAEUGS': 'tation',
        'O*R': "or",
#        '-L': "'ll",
    }

    for outline, word in dictionary.items():
        last_stroke = outline.split('/')[-1]
        base_outline = '/'.join(outline.split('/')[:-1])

        if base_outline not in dictionary:
            continue

        base_word = dictionary[base_outline]
        suffix = suffixes.get(last_stroke)

        if suffix and orthography.combine(base_word, suffix) == word:
            #print('deleting', outline, word, '=', base_word, "+", suffix)
            del new_dictionary[outline]

    return new_dictionary


def filter_common_affixes(dictionary):
    return filter_common_suffixes(filter_common_prefixes(dictionary))


def filter_infolds(dictionary):
    new_dictionary = copy(dictionary)

    infolds = {
        'S': 's',
        'Z': 's',
        'G': 'ing',
        'D': 'ed',
    }
    for outline, word in dictionary.items():
        for infold, suffix in infolds.items():
            if outline.endswith(infold):
                base_outline = outline[:-len(infold)]
                base_word = dictionary.get(base_outline, '')
                if orthography.combine(base_word, suffix) == word:
                    #print('deleting infold', outline, word)
                    del new_dictionary[outline]

    return new_dictionary


def can_pronounce(word):
    return word in CMUDICT


STENO_DICTIONARIES_URL = 'https://raw.githubusercontent.com/didoesdigital/steno-dictionaries/62e3c35ef4ee5508dd625acac3b036e4a4c20ed7'

def filter_mistakes(dictionary):
    new_dictionary = copy(dictionary)

    bad_habits_dictionary = load_net_dictionary(f'{STENO_DICTIONARIES_URL}/dictionaries/bad-habits.json')
    misstrokes_dictionary = load_net_dictionary(f'{STENO_DICTIONARIES_URL}/dictionaries/misstrokes.json')

    for outline in bad_habits_dictionary:
        if outline in new_dictionary:
            del new_dictionary[outline]

    for outline in misstrokes_dictionary:
        if outline in new_dictionary:
            del new_dictionary[outline]

    return new_dictionary


def canonicalize_outline(dictionary):
    new_dictionary = copy(dictionary)

    outlines_by_word = defaultdict(lambda: [])

    for outline, word in dictionary.items():
        outlines_by_word[word].append(outline)

    for word, outlines in sorted(outlines_by_word.items(), reverse=True, key=lambda pair: len(pair[1])):
        if len(outlines) > 1:
#            print(word, 'deleting', len(outlines), 'outlines, keeping', outlines[0])
            for outline in outlines[1:]:
                del new_dictionary[outline]

    return new_dictionary


def main():
    dictionary = load_main_dictionary()
    save_dictionary('main', dictionary)

    stage = 0
    dictionary = filter_valid_outlines(dictionary)
    save_dictionary(f'{stage:02}.main', dictionary)

    stage += 1
    dictionary = filter_briefs(dictionary)
    save_dictionary(f'{stage:02}.main', dictionary)

    stage += 1
    affix_dictionary, dictionary = split_dictionary(dictionary, is_affix)
    save_dictionary(f'{stage:02}.main', dictionary)
    save_dictionary(f'affix_dictionary', affix_dictionary)

    stage += 1
    proper_dictionary, dictionary = split_dictionary(dictionary, is_proper_noun)
    save_dictionary(f'{stage:02}.main', dictionary)
    save_dictionary('proper_dictionary', proper_dictionary)

    stage += 1
    punctuation_dictionary, dictionary = split_dictionary(dictionary, has_punctuation)
    save_dictionary(f'{stage:02}.main', dictionary)
    save_dictionary('punctuation_dictionary', punctuation_dictionary)

    stage += 1
    multiword_dictionary, dictionary = split_dictionary(dictionary, is_multiword)
    save_dictionary(f'{stage:02}.main', dictionary)
    save_dictionary('multiword_dictionary', multiword_dictionary)

    stage += 1
    dictionary = filter_common_affixes(dictionary)
    save_dictionary(f'{stage:02}.main', dictionary)

    stage += 1
    dictionary, cant_pronounce_dictionary = split_dictionary(dictionary, can_pronounce)
    save_dictionary(f'{stage:02}.main', dictionary)
    save_dictionary('cant_pronounce', cant_pronounce_dictionary)

    stage += 1
    dictionary = filter_infolds(dictionary)
    save_dictionary(f'{stage:02}.main', dictionary)

    stage += 1
    dictionary = filter_mistakes(dictionary)
    save_dictionary(f'{stage:02}.main', dictionary)

#    stage += 1
#    dictionary = canonicalize_outline(dictionary)
#    save_dictionary(f'{stage:02}.main', dictionary)

    save_dictionary('final', dictionary)

    shutil.copyfile('output/final.json', 'dictionaries/base.json')


if __name__ == "__main__":
    main()
