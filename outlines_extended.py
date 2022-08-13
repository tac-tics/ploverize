LEFTS = "STKPWHR"
RIGHTS = "FRPBLGTSDZ"
MIDDLES = "AO*EU"

def stroke_to_keys(stroke):
    keys = []
    i = 0
    while i < len(stroke):
        key = stroke[i]
        i += 1
        while i < len(stroke) and stroke[i].upper() != stroke[i]:
            key += stroke[i]
            i += 1
        keys.append(key)

    return keys

assert stroke_to_keys('BAwS') == ['B', 'Aw', 'S']
assert stroke_to_keys('GREeN') == ['G', 'R', 'Ee', 'N']
assert stroke_to_keys('MYNg') == ['M', 'Y', 'Ng']
assert stroke_to_keys('R-Z') == ['R', '-', 'Z']
assert stroke_to_keys('BEyeK') == ['B', 'Eye', 'K']


def split_stroke(stroke):
    keys = stroke_to_keys(stroke)
    mode = 'left'

    middles = ['A', 'O', 'I', 'Ee', 'E', 'U', '*', 'Aw', 'Ow', 'Eye', 'Oo', 'Ea', 'Oh']
    left = []
    middle = []
    right = []

    for key in keys:
        if mode == 'left':
            if key == '-':
                mode = 'right'
            elif key in middles:
                mode = 'middle'
            else:
                left.append(key)

        if mode == 'middle':
            if key not in middles:
                mode = 'right'
            else:
                middle.append(key)

        if mode == 'right':
            right.append(key)

    if len(middle) == 0 and len(right) > 0:
        # trim leading '-'
        right = right[1:]

    return ''.join(left), ''.join(middle), ''.join(right)


assert split_stroke('GREeN') == ('GR', 'Ee', 'N')
assert split_stroke('GR-N') == ('GR', '', 'N')
assert split_stroke('-N') == ('', '', 'N')
assert split_stroke('N') == ('N', '', '')


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
assert is_valid_side('TKPW', LEFTS)
assert is_valid_side('*', MIDDLES)
assert is_valid_side('G', RIGHTS)


def is_valid_stroke(stroke):
    left, middle, right = split_stroke(stroke)
    return (
        is_valid_side(left, LEFTS) and
        is_valid_side(middle, MIDDLES) and
        is_valid_side(right, RIGHTS)
    )


assert is_valid_stroke('SRA')
assert is_valid_stroke('-Z')
assert is_valid_stroke('TKPW*G')


def is_valid_outline(outline):
    strokes = outline.split('/')
    return all(is_valid_stroke(stroke) for stroke in strokes)

assert is_valid_outline('SRA/-Z')
assert is_valid_outline('TKPW*G')


def stroke_to_simple(stroke):
    left, middle, right = split_stroke(stroke)
    left = (
        left
            .replace('Y', 'KWR')
            .replace('J', 'SKWR')
            .replace('G', 'TKPW')
            .replace('N', 'TPH')
            .replace('M', 'PH')
            .replace('V', 'HR')
            .replace('B', 'PW')
            .replace('D', 'TK')
            .replace('F', 'TP')
    )

    middle = (
        middle
            .replace('Ee', 'AOE')
            .replace('I', 'EU')
            .replace('Aw', 'AU')
            .replace('Ow', 'OU')
            .replace('Oh', 'OE')
            .replace('Eye', 'AOEU')
    )

    right = (
        right
            .replace('N', 'PB')
            .replace('M', 'PL')
            .replace('V', 'F')
            .replace('Ck', 'BG')
            .replace('Ng', 'PBG')
    )

    if middle == '' and right != '':
        middle = '-'

    return left + middle + right


def to_simple(outline):
    strokes = outline.split('/')
    new_outline = '/'.join(stroke_to_simple(s) for s in strokes)
    assert is_valid_outline(new_outline), f'{new_outline} is invalid (original is {outline})'
    return new_outline


assert to_simple('GREeN') == 'TKPWRAOEPB'