import json
import sys
from lib.load import (
    load_main_dictionary,
    load_lapwing_dictionary,
)

main_dictionary = load_main_dictionary()
lapwing_dictionary = load_lapwing_dictionary()


def lookup(word):
    main_outlines = set(outline for (outline, w) in main_dictionary.items() if w == word)
    lapwing_outlines = set(outline for (outline, w) in lapwing_dictionary.items() if w == word)

    boths = main_outlines.intersection(lapwing_outlines)

#    if len(boths) == 1:
#        print(f'    "{list(boths)[0]}": "{word}",')

    print('Both')
    for outline in main_outlines.intersection(lapwing_outlines):
        print('   ', outline)

    print()
    print('main.json')
    for outline in main_outlines.difference(lapwing_outlines):
        print('   ', outline)


    print()
    print('lapwing.json')
    for outline in lapwing_outlines.difference(main_outlines):
        print('   ', outline)


def main():
    word = sys.argv[1]

    with open('output/main.words.json') as infile:
        words = json.load(infile)

    lookup(word)




if __name__ == "__main__":
    main()
