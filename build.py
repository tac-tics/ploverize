from copy import copy
from pathlib import Path
from collections import defaultdict
import sys
import json
import string
import shutil
import os.path

import nltk

import dict_from_base
import lib.orthography as orthography
import lib.outlines_extended as outlines_extended
import lib.outline
from lib.load import (
    load_net_dictionary,
    load_main_dictionary,
    load_lapwing_dictionary,
    save_dictionary,
    load_dictionary_path,
)

def to_simple(dictionary):
    new_dictionary = {}
    for outline, word in dictionary.items():
        simple_outline = outlines_extended.to_simple(outline)
        new_dictionary[simple_outline] = word
    return new_dictionary


CMUDICT = nltk.corpus.cmudict.dict()


def unique_briefs(dictionary):
    new_dictionary = copy(dictionary)

    with open('output/briefs.json') as infile:
        briefs_dictionary = json.load(infile)

    for brief_outline, brief_word in briefs_dictionary.items():
        for outline, word in dictionary.items():
            if word == brief_word and outline in new_dictionary and outline != brief_outline:
                del new_dictionary[outline]

    return new_dictionary


def unique_single_strokes(dictionary):
    EXCEPTIONS = ['-S', '-Z', '-RS', '-RZ']
    new_dictionary = copy(dictionary)

    outlines_by_word = defaultdict(lambda: [])
    for outline, word in dictionary.items():
        if outline in EXCEPTIONS:
            continue

        strokes = outline.split('/')
        if len(strokes) == 1:
            outlines_by_word[word].append(outline)

    for word in list(outlines_by_word.keys()):
        outlines = outlines_by_word[word]
        if len(outlines) > 1:
            #print(word, outlines)
            pass

#    for brief_outline, brief_word in briefs_dictionary.items():
#        for outline, word in dictionary.items():
#            if word == brief_word and outline in new_dictionary and outline != brief_outline:
#                del new_dictionary[outline]

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


def has_apostrophe(word):
    ALLOWED = [
        "s'more",
        "c'mon",
        "ne'er do well",
        "y'all",
        "young'un",
        "o'clock",
        "ma'am",
        "movie 'til",
        "{mid-'^}",
        "mid-'60s",
        "rock 'n' roll",
        "'50s",
        "'60s",
        "'70s",
        "'60",
        "{^s'}",
        "{O'^}",
        "{o'^}",
        "o'er",
    ]

    return "'" in word and word not in ALLOWED

def has_nonsense(word):
    letters = [l for l in string.ascii_letters] + ['-', "'"]
    return any(ch not in letters for ch in word)


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


STENO_DICTIONARIES_URL = 'https://raw.githubusercontent.com/didoesdigital/steno-dictionaries/62e3c35ef4ee5508dd625acac3b036e4a4c20ed7'

def filter_mistakes(dictionary):
    new_dictionary = copy(dictionary)

    bad_habits_dictionary = load_net_dictionary(f'{STENO_DICTIONARIES_URL}/dictionaries/bad-habits.json')
    misstrokes_dictionary = load_net_dictionary(f'{STENO_DICTIONARIES_URL}/dictionaries/misstrokes.json')

    for outline in bad_habits_dictionary:
        if outline in new_dictionary:
            word = new_dictionary[outline]
            del new_dictionary[outline]
            #print(f"Removing bad habit {outline.ljust(15)} {word}")

    for outline in misstrokes_dictionary:
        if outline in new_dictionary:
            word = new_dictionary[outline]
            del new_dictionary[outline]
            #print(f"Removing misstroke {outline.ljust(15)} {word}")

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


def combine_dictionaries(dictionaries):
    new_dictionary = copy(dictionaries[0])
    for dictionary in dictionaries[1:]:
        for outline, word in dictionary.items():
            if outline in new_dictionary and outline != "":
                old_word = new_dictionary[outline]
                if word == old_word:
                    warning = ''
                else:
                    warning = '(was: ' + old_word + ')'
                print('Duplicated entry:', outline, word, warning)
            new_dictionary[outline] = word
    return new_dictionary


def clean_output_dir():
    print('* Cleaning output/ directory...')
    output_dir = Path('output/').resolve()
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir()


def only_uniques(dictionary):
    new_dictionary = {}
    outlines_by_word = defaultdict(lambda: [])

    for outline, word in dictionary.items():
        outlines_by_word[word].append(outline)

    for word, outlines in outlines_by_word.items():
        if len(outlines) == 1:
            outline = outlines[0]
            new_dictionary[outline] = word

    return new_dictionary


def add_henkan_bypass(dictionary, main_dictionary):
    new_dictionary = copy(dictionary)

    w = load_dictionary_path('output/main.words.json')
    for outline, word in main_dictionary.items():
        if word not in w:
            continue

        #new_outline = outline + '/#'
        new_outline = outline
        new_dictionary[new_outline] = word

    return new_dictionary

with open('output/main.words.json') as infile:
    MAIN_WORDS = json.load(infile)


def make_mobility_dictionary():
    d = {
        "-Z": "{^}{#Return}{^}{-|}",

        "-D": "{#BackSpace}",
        "AD": "{#Control(BackSpace)}",
        "S-D": "{#Shift(BackSpace)}",

        "R": "{#Tab}",
        "AR": "{#Control(Tab)}",
        "S-R": "{#Shift(Tab)}",

        "-R": "{#Left}",
        "-B": "{#Down}",
        "-P": "{#Up}",
        "-G": "{#Right}",

        "AR": "{#Control(Left)}",
        "AB": "{#Control(Down)}",
        "AP": "{#Control(Up)}",
        "AG": "{#Control(Right)}",

        "S-R": "{#Shift(Left)}",
        "S-B": "{#Shift(Down)}",
        "S-P": "{#Shift(Up)}",
        "S-G": "{#Shift(Right)}",

        "SAR": "{#Shift(Control(Left))}",
        "SAB": "{#Shift(Control(Down))}",
        "SAP": "{#Shift(Control(Up))}",
        "SAG": "{#Shift(Control(Right))}",
    }

    return {
        "exclude_entry": False,
        "exit_on_mismatch": False,
        "exit_on_match": False,
        "ignore_folding": True,
        'entry': {
            '+PH': '{#}',
        },
        'exit': {
            '+': '{#}',
        },
        'dict': d,
    }


def make_fingerspelling_dictionary():
    FINGER_SPELLING = {
        'a': 'A',
        'b': 'PW',
        'c': 'KR',
        'd': 'TK',
        #'e': 'E',
        'e': 'RO',
        'f': 'TP',
        'g': 'TKPW',
        'h': 'H',
        # 'i': 'EU',
        'i': 'RAO',
        'j': 'SKWR',
        'k': 'K',
        'l': 'HR',
        'm': 'PH',
        'n': 'TPH',
        'o': 'O',
        'p': 'P',
        'q': 'KW',
        'r': 'R',
        's': 'S',
        't': 'T',
        #'u': 'U',
        'u': 'RA',
        'v': 'SR',
        'w': 'W',
        'x': 'KP',
        'y': 'KWR',
        'z': 'TW',

        '0': '-Z',
        '1': '-F',
        '2': '-P',
        '3': '-L',
        '4': '-T',
        '5': '-D',
        '6': '-R',
        '7': '-B',
        '8': '-G',
        '9': '-S',
        ',': 'E',
        '.': 'U',
    }

    new_dictionary = {}
    for ch, outline in FINGER_SPELLING.items():
        lowerword = '{>}{&' + ch + '}'
        new_dictionary[outline] = lowerword

        if ch in string.ascii_lowercase:
            upperword = '{&' + ch.upper() + '}'
            new_dictionary[outline + '*'] = upperword

    new_dictionary['SP'] = '{^ ^}'
    new_dictionary['-PS'] = '{^ ^}'
    new_dictionary['*'] = '=undo'

    return {
        "exclude_entry": False,
        "exit_on_mismatch": False,
        "exit_on_match": False,
        "ignore_folding": True,
        "entry": {
            "+TP": "{#}"
        },
        "exit": {
            "+": "{#}"
        },
        'dict': new_dictionary,
    }


def main():
    #clean_output_dir()

    main_dictionary = load_main_dictionary()
    save_dictionary('output/main.json', main_dictionary)

    lapwing_dictionary = load_lapwing_dictionary()
    save_dictionary('output/lapwing.json', lapwing_dictionary)

    #dictionary = {}
    #dictionary = only_uniques(partition_main(main_dictionary))
    #dictionary = add_henkan_bypass(dictionary, main_dictionary)

#    for outline, word in lapwing_dictionary.items():
#        if word in MAIN_WORDS:
#            dictionary[outline] = word

    dictionary = dict_from_base.build_dict()

    stage = 0
#    dictionary = filter_mistakes(dictionary)
#    save_dictionary(f'output/{stage:02}.main.json', dictionary)

    # make sure this just loads, okay?
#    personal_dictionary = load_dictionary_path('dictionaries/main.dict')
#    canonical_outlines = {}
#    for outline, word in personal_dictionary.items():
#        canonical_outlines[word] = outline
#
#    d = to_simple(personal_dictionary)
#    with open('output/briefs.json', 'w') as outfile:
#        json.dump(d, outfile)

#    p = load_dictionary_path('output/main.proper.json')
#    for outline, word in main_dictionary.items():
#        if word not in p:
#            continue
#
#        if word.startswith('to '):
#            # wtf are even these wtf
#            continue
#
#        strokes = outline.split('/')
#        if strokes[0] == '-T':
#            strokes[0] = 'T-P'
#        else:
#            strokes = ['-P'] + strokes
#        new_outline = '/'.join(strokes)
#        dictionary[new_outline] = word

    stage += 1
    dictionary_files = [
#        'output/briefs.json',
        'dictionaries/affixes.json',
        'dictionaries/commands.json',
        'dictionaries/punctuation.json',
        'dictionaries/machine.json',
#        'dictionaries/misc.json',
    ]
    dictionaries = [dictionary] + [load_dictionary_path(d) for d in dictionary_files]
    dictionary = combine_dictionaries(dictionaries)
    save_dictionary(f'output/{stage:02}.main.json', dictionary)

#    stage += 1
#    new_dictionary = {}
#    for outline, word in dictionary.items():
#        if word == '{#}':
#            continue
#
#        if word in canonical_outlines:
#            canonical_outline = canonical_outlines[word]
#            if outline != outlines_extended.to_simple(canonical_outline):
#                word = f'[Use {canonical_outline} for {word!r}]'
#
#        new_dictionary[outline] = word
#    dictionary = new_dictionary
#    save_dictionary(f'output/{stage:02}.main.json', dictionary)

#    stage += 1
#    dictionary = unique_briefs(dictionary)
#    save_dictionary(f'output/{stage:02}.main.json', dictionary)
#
#    stage += 1
#    dictionary = unique_single_strokes(dictionary)
#    save_dictionary(f'output/{stage:02}.main.json', dictionary)

#    stage += 1
#    dictionary = canonicalize_outline(dictionary)
#    save_dictionary(f'output/{stage:02}.main.json', dictionary)

#    stage += 1
#    dictionary = add_fingerspelling(dictionary)
#    save_dictionary(f'output/{stage:02}.main.json', dictionary)

    save_dictionary('output/final.json', dictionary)

    save_dictionary(f'output/fingerspelling.modal', make_fingerspelling_dictionary())
    save_dictionary(f'output/mobility.modal', make_mobility_dictionary())


if __name__ == "__main__":
    main()
