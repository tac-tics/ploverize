import nltk


cmudict = nltk.corpus.cmudict.dict()


VOWELS = [
    'AA',
    'AE',
    'AH',
    'AO',
    'AW',
    'AY',
    'EH',
    'ER',
    'EY',
    'IH',
    'IY',
    'OW',
    'OY',
    'UH',
    'UW',
]


def consonant_clusters_in_pronunciation(pronunciation):
    clusters = [[]]
    for sound in pronunciation:
        if any(sound.startswith(vowel) for vowel in VOWELS):
            clusters.append([])
        else:
            cluster = clusters[-1]
            cluster.append(sound)
    return [c for c in clusters if c]


CLUSTERS = set()
CLUSTER_EXAMPLES = {}

for word, pronunciations in cmudict.items():
    pronunciation = pronunciations[0]
    clusters = consonant_clusters_in_pronunciation(pronunciation)
    for cluster in clusters:
        CLUSTERS.add(' '.join(cluster))
        CLUSTER_EXAMPLES[' '.join(cluster)] = word


for cluster in sorted(CLUSTERS):
    example = CLUSTER_EXAMPLES[cluster]
    print(cluster.ljust(10), example)
