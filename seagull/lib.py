import typing as t
from dataclasses import dataclass


@dataclass
class Entry:
    mnemonic: str
    word: str
    cat: t.List[str]
    rel: t.List[str]
    notes: str

    def outline(self) -> str:
        strokes = []
        for mnemonic_stroke in self.mnemonic.split('/'):
            stroke = MnemonicStroke.make(mnemonic_stroke)
            regular_stroke = stroke.regular()
            strokes.append(regular_stroke)

        return '/'.join(strokes)


def read_entry(infile):
    line = infile.readline()
    while line.startswith('#'):
        line = infile.readline()
    while not line.strip():
        if line == '':
            return None

        line = infile.readline()

    mnemonic, *word_parts = line.strip().split(' ')
    word = ' '.join(word_parts)
    cat = []
    rel = []

    note_lines = []
    line = infile.readline().rstrip()
    while line != '---':
        assert line[:4] == '    '
        line = line.strip()

        if line.startswith('cat: '):
            cat = line[5:].split(' ')
        elif line.startswith('rel: '):
            rel = line[5:].split(' ')
        else:
            note_lines.append(line[4:])

        line = infile.readline().rstrip()

    notes = '\n'.join(note_lines).strip()

    return Entry(
        mnemonic=mnemonic,
        word=word,
        cat=cat,
        rel=rel,
        notes=notes,
    )

INITIALS: t.Dict[str, str] = {}
MIDDLES: t.Dict[str, str] = {}
FINALS: t.Dict[str, str] = {}

def load_layout():
    global INITIALS
    global MIDDLES
    global FINALS

    with open('layout/initials.txt') as infile:
        for line in infile:
            i = line.index(' ')
            part = line[:i].strip()
            keys = line[i:].strip()

            assert part not in INITIALS, f'Duplicate found in initials.txt {part}'

            INITIALS[part] = keys

    with open('layout/middles.txt') as infile:
        for line in infile:
            i = line.index(' ')
            part = line[:i].strip()
            keys = line[i:].strip()

            assert part not in MIDDLES, f'Duplicate found in middles.txt {part}'

            MIDDLES[part] = keys

    with open('layout/finals.txt') as infile:
        for line in infile:
            i = line.index(' ')
            part = line[:i].strip()
            keys = line[i:].strip()

            assert part not in FINALS, f'Duplicate found in finals.txt {part}'

            FINALS[part] = keys


load_layout()


@dataclass
class MnemonicStroke:
    initial: str
    middle: str
    final: str

    @staticmethod
    def make(stroke: str) -> 'MnemonicStroke':
        initial_stroke = stroke
        part = MnemonicStroke._consume_part(stroke)

        if part in INITIALS:
            initial = part
            stroke = stroke[len(part):]
            part = MnemonicStroke._consume_part(stroke)
        else:
            initial = ''

        had_dash = False
        if part in MIDDLES or part == '-':
            if part == '-':
                had_dash = True

            middle = part if not had_dash else ''

            stroke = stroke[len(part):]
            part = MnemonicStroke._consume_part(stroke)
        else:
            middle = ''

        if part in FINALS:
            final = part
            stroke = stroke[len(part):]
            part = MnemonicStroke._consume_part(stroke)
        else:
            final = ''

        assert stroke == '', f"There's a part of the stroke {initial_stroke!r} that is unaccounted for: {stroke!r}"
        if middle == '' and final != '':
            assert had_dash, f'If an empty middle with a non-empty final requres a dash: ' + initial + '-' + final

        return MnemonicStroke(
            initial=initial,
            middle=middle,
            final=final,
        )


    @staticmethod
    def _consume_part(stroke: str) -> str:
        if len(stroke) == 0:
            return ''

        assert stroke[0].isupper() or stroke[0] == '-', f"First letter had an issue: {stroke!r}"
        i = 1
        while i < len(stroke) and stroke[i].islower():
            i += 1

        return stroke[:i]

    def split(self) -> t.Tuple[str, str, str]:
        return (self.initial, self.middle, self.final)

    @staticmethod
    def is_valid(stroke: str) -> bool:
        try:
            MnemonicStroke.make(stroke)
            return True
        except AssertionError:
            return False

    def regular(self) -> str:
        initial, middle, final = self.split()

        initial_keys = INITIALS.get(initial, '')
        middle_keys = MIDDLES.get(middle, '')
        final_keys = FINALS.get(final, '')

        if middle_keys == '' and final_keys != '':
            middle_keys = '-'

        return f"{initial_keys}{middle_keys}{final_keys}"


assert MnemonicStroke.make('DisAyTion').split() == ('Dis', 'Ay', 'Tion')
assert MnemonicStroke.make('AyTion').split() == ('', 'Ay', 'Tion')
assert MnemonicStroke.make('-Tion').split() == ('', '', 'Tion')


ENTRIES_BY_MNEMONIC = {}
ENTRIES_BY_OUTLINE = {}
ENTRIES_BY_WORD = {}


assert MnemonicStroke.make('-Bing').regular() != ''


def load_entries():
    global ENTRIES_BY_OUTLINE
    global ENTRIES_BY_WORD

    with open('main.dict') as infile:
        entry = read_entry(infile)
        while entry is not None:
            strokes = entry.mnemonic.split('/')
            for stroke in strokes:
                assert MnemonicStroke.is_valid(stroke), f'Invalid mnemonic for {entry.mnemonic} {entry.word}'

            assert entry.word not in ENTRIES_BY_WORD, f'Word already exists: {entry.word}'
            assert entry.mnemonic not in ENTRIES_BY_MNEMONIC, f'Mnemonic already exists: {entry.mnemonic}'
            assert entry.outline() not in ENTRIES_BY_OUTLINE, f'Outline already exists: {entry.outline()} from {entry.mnemonic}'

            ENTRIES_BY_MNEMONIC[entry.mnemonic] = entry
            ENTRIES_BY_WORD[entry.word] = entry
            ENTRIES_BY_OUTLINE[entry.outline()] = entry
            entry = read_entry(infile)


load_entries()

for outline, entry in ENTRIES_BY_OUTLINE.items():
    print(outline, entry.word)
