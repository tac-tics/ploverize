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

