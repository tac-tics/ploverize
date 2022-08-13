from pathlib import Path
import sys
from collections import defaultdict
import string
import os.path
import httpx
import json
import orthography
from copy import copy
import nltk
import shutil
import outlines_extended


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


def load_dictionary_path(filename):
    with open(filename) as infile:
        return json.load(infile)



def simplify_stroke(stroke):
    left, middle, right = split_stroke(stroke)
    left = (
        left
            .replace('V', 'SR')
            .replace('N', 'TPH')
    )
    middle = (
        middle
            .replace('Y', 'EU')
    )
    return join_stroke(left, middle, right)


def simplify_outline(outline):
    strokes = outline.split('/')
    return '/'.join(simplify_stroke(s) for s in strokes)


def to_simple(dictionary):
    new_dictionary = {}
    for outline, word in dictionary.items():
        simple_outline = outlines_extended.to_simple(outline)
        new_dictionary[simple_outline] = word
    return new_dictionary


CMUDICT = nltk.corpus.cmudict.dict()


LEFTS = "STKPWHR"
RIGHTS = "FRPBLGTSDZ"
MIDDLES = "AO*EU"


def join_stroke(left, middle, right):
    if middle == '' and right != '':
        middle = '-'

    return left + middle + right


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


def split_valid_outlines(dictionary):
    valid_outlines_dict = {}
    invalid_outlines_dict = {}
    for outline, word in dictionary.items():
        if is_valid_outline(outline):
            valid_outlines_dict[outline] = word
        else:
            invalid_outlines_dict[outline] = word
    return valid_outlines_dict, invalid_outlines_dict


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


def is_affix(word):
    return word.startswith('{^') or word.endswith('^}')


word_letters = [l for l in string.ascii_letters] + ["'", "-", " ", "."]


def has_punctuation(word):
    return not all(ch in word_letters for ch in word)
#    return any(ch in word for ch in '.,?/:;[]^&%$#@!(){}<>')


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


def is_proper_noun(word):
    allowed = ["I", "I'll", "I'm", "I'd", "I've"]
    has_uppercase_letter = any(ch in string.ascii_uppercase for ch in word)
    contains_allowed_word = any(p == w for p in word.split(' ') for w in allowed)
    return has_uppercase_letter and not contains_allowed_word


def is_numeric(word):
    return any(digit in word for digit in string.digits)


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


SUFFIXES = [
    "'ll",
    "'s",
    "'ve",
    "n't",

    'ing',
    'ed',
    'er',
    'ers',
    'ly',
    's',
    'ier',

#    "le",
#    "or",
#    'ability',
#    'able',
#    'al',
#    'ary',
#    'ation',
#    'ble',
#    'bly',
#    'cal',
#    'cy',
#    'ial',
#    'ian',
#    'ibility',
#    'ic',
#    'ically',
#    'in',
#    'iness',
#    'ion',
#    'is',
#    'ism',
#    'ist',
#    'ity',
#    'ive',
#    'l',
#    'lar',
#    'less',
#    'ment',
#    'ness',
#    'ry',
#    'ship',
#    'tation',
#    'tion',
#    'tive',
#    'tory',
#    'ty',
#    'uous',
#    'y',
]


def filter_common_suffixes(dictionary):
    new_dictionary = copy(dictionary)
    suffixes = {}

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
            suffixes[outline] = word

    for outline, word in dictionary.items():
        if outline not in new_dictionary:
            continue

        for ending in ['ing', 'ly']:
            if word.endswith(ending):
                del new_dictionary[outline]
                suffixes[outline] = word
                break

    return new_dictionary, suffixes


def split_common_affixes(dictionary):
    new_dictionary, suffixes = filter_common_suffixes(filter_common_prefixes(dictionary))
    return new_dictionary, suffixes


def split_infolds(dictionary):
    new_dictionary = copy(dictionary)
    infolds_dictionary = {}

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
                    infolds_dictionary[outline] = word

    return new_dictionary, infolds_dictionary


def can_pronounce(word):
    return word in CMUDICT


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


def partition_main(main_dictionary):
    print('* Partitioning Main Dictionary')

    words = set(main_dictionary.values())

    letters = set(w for w in words if len(w) == 1 and w != 'a' and w != 'I')
    words = words.difference(letters)
    save_dictionary('main.letters', sorted(letters))
    print('Created main.letters')

    affixes = set(w for w in words if is_affix(w))
    words = words.difference(affixes)
    save_dictionary('main.affixes', sorted(affixes))
    print('Created main.affixes')

    punctuation = set(w for w in words if has_punctuation(w))
    words = words.difference(punctuation)
    save_dictionary('main.punctuation', sorted(punctuation))
    print('Created main.punctuation')

    # How many of these have a Wikipedia page?
    proper_nouns = set(w for w in words if is_proper_noun(w))
    words = words.difference(proper_nouns)
    save_dictionary('main.proper', sorted(proper_nouns))
    print('Created main.proper')

    multiword = set(w for w in words if ' ' in w)
    words = words.difference(multiword)
    save_dictionary('main.multiword', sorted(multiword))
    print('Created main.multiword')

    numeric = set(w for w in words if is_numeric(w))
    words = words.difference(numeric)
    save_dictionary('main.numeric', sorted(numeric))
    print('Created main.numeric')

    cant_pronounce = set(w for w in words if not can_pronounce(w))
    words = words.difference(cant_pronounce)
    save_dictionary('main.cant_pronounce', sorted(cant_pronounce))
    print('Created main.cant_pronounce')

    inflections = set()

    for word in sorted(words, key=lambda w: (len(w), w)):
        for suffix in SUFFIXES:
            inflected_word = orthography.combine(word, suffix)
            if inflected_word in words:
                inflections.add(inflected_word)

    save_dictionary('main.inflections', sorted(inflections))
    words = words.difference(inflections)
    print('Created main.inflections')

    save_dictionary('main.words', sorted(words))
    print('Created main.words')

    new_dictionary = {}
    for outline, word in main_dictionary.items():
        if word in words:
            new_dictionary[outline] = word

    return new_dictionary


def clean_output_dir():
    print('* Cleaning output/ directory...')
    output_dir = Path('output/').resolve()
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir()




def main():
    clean_output_dir()

    main_dictionary = load_main_dictionary()
    save_dictionary('main', main_dictionary)

    dictionary = partition_main(main_dictionary)

    stage = 0
    dictionary = filter_mistakes(dictionary)
    save_dictionary(f'{stage:02}.main', dictionary)

    # make sure this just loads, okay?
    personal_dictionary = load_dictionary_path('dictionaries/main.dict')
    canonical_outlines = {}
    for outline, word in personal_dictionary.items():
        canonical_outlines[word] = outline

    d = to_simple(personal_dictionary)
    with open('output/briefs.json', 'w') as outfile:
        json.dump(d, outfile)

    p = load_dictionary_path('output/main.proper.json')
    for outline, word in main_dictionary.items():
        if word not in p:
            continue

        if word.startswith('to '):
            # wtf are even these wtf
            continue

        strokes = outline.split('/')
        if strokes[0] == '-T':
            strokes[0] = 'TP'
        else:
            strokes = ['P'] + strokes
        new_outline = '/'.join(strokes)
        dictionary[new_outline] = word

    stage += 1
    dictionary_files = [
        'output/briefs.json',
        'dictionaries/affixes.json',
        'dictionaries/commands.json',
        'dictionaries/fingerspelling.json',
        'dictionaries/numbers.json',
        'dictionaries/punctuation.json',
        'dictionaries/machine.json',
        'dictionaries/misc.json',
    ]
    dictionaries = [dictionary] + [load_dictionary_path(d) for d in dictionary_files]
    dictionary = combine_dictionaries(dictionaries)
    save_dictionary(f'{stage:02}.main', dictionary)

    stage += 1
    new_dictionary = {}
    for outline, word in dictionary.items():
        if word == '{#}':
            continue

        if word in canonical_outlines:
            canonical_outline = canonical_outlines[word]
            if outline != outlines_extended.to_simple(canonical_outline):
                word = f'[Use {canonical_outline} for {word!r}]'

        new_dictionary[outline] = word
    dictionary = new_dictionary
    save_dictionary(f'{stage:02}.main', dictionary)

    stage += 1
    dictionary = unique_briefs(dictionary)
    save_dictionary(f'{stage:02}.main', dictionary)

    stage += 1
    dictionary = unique_single_strokes(dictionary)
    save_dictionary(f'{stage:02}.main', dictionary)

#    stage += 1
#    dictionary = canonicalize_outline(dictionary)
#    save_dictionary(f'{stage:02}.main', dictionary)

    save_dictionary('final', dictionary)


if __name__ == "__main__":
    main()
