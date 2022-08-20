from lib.outlines_extended import to_simple
import json


def resolve_outline(ext_outline, entries_by_word):
    if ext_outline.startswith('['):
        end_idx = ext_outline.index(']')
        reference_word = ext_outline[1:end_idx]
        base_entry = entries_by_word[reference_word]
        base_outline = resolve_outline(base_entry['outline'], entries_by_word)
        return to_simple(base_outline + ext_outline[end_idx+1:])
    else:
        return to_simple(ext_outline)

def get_entries_by_word():
    with open('dictionaries/base.json') as infile:
        entries = json.load(infile)

    entries_by_word = {}

    for entry in entries:
        if not entry.get('outline'):
            continue

        word = entry['word']
        assert word not in entries_by_word, f"Word is defined twice: {word}"
        entries_by_word[word] = entry

    return entries_by_word


def main():
    entries_by_word = get_entries_by_word()

    dictionary = {}

    for word, entry in entries_by_word.items():
        word = entry['word']
        ext_outline = entry['outline']
        print(word.ljust(20), resolve_outline(ext_outline, entries_by_word))


if __name__ == '__main__':
    main()
