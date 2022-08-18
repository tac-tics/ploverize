import json
import httpx


def load_net_dictionary(url):
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def load_main_dictionary():
    url = 'https://raw.githubusercontent.com/openstenoproject/plover/1e4d8b3bff0b705d936f14d31d5997456c5823cf/plover/assets/main.json'
    return load_net_dictionary(url)


def load_lapwing_dictionary():
    url = 'https://raw.githubusercontent.com/aerickt/steno-dictionaries/6a0e3c844aec96a3d11350ef7a189f1ef03b243f/lapwing-base.json'
    return load_net_dictionary(url)


def save_dictionary(name, dictionary):
    filename = f'{name}'

    with open(filename, 'w') as outfile:
        json.dump(dictionary, outfile, indent=4, ensure_ascii=False)


def load_dictionary_path(filename):
    with open(filename) as infile:
        return json.load(infile)
