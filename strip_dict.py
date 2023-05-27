words = set()



with open('output/dict.txt') as infile:
    for line in infile:
        word = line.strip()
        words.add(word)

with open('nonbase_words.txt') as infile:
    for line in infile:
        word = line.strip()
        if word in words:
            words.remove(word)

for word in sorted(words):
    print(word)
