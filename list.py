import json

with open('output/main.words.json') as infile:
    words = json.load(infile)

for word in words:
    if len(word) == 3:
        print(word)
