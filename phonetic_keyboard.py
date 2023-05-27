import itertools


LEFTS = "STKPWHR"
RIGHTS = "FRPBLGTSDZ"


def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return itertools.chain.from_iterable(itertools.combinations(xs,n) for n in range(len(xs)+1))


for s in powerset(RIGHTS):
    print(''.join(s))







#LEFT_COMBOS = {
#    "TK": "D",
#    "PW": "B",
#    "HR": "L",
#    "KH": "CH",
#    "PH": "M",
#    "TPH": "N",
#    "TP": "F",
#    "TKPW": "G",
#    "SKWR": "J",
#    "KWR": "Y",
#    "GS": "SHUN",
##    "RBS": "SHS",
##    "KP": "X",
#}
#
#RIGHT_COMBOS = {
#    "BG": "K",
#    "FP": "CH",
#    "PL": "M",
#    "PB": "N",
#    "SR": "V",
#    "PBLG", "J",
#}


