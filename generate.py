import json
import sys
import random


def load_words(file_name):
    with open(file_name, 'r') as handle:
        raw = handle.read()
        data = json.loads(raw)
        # TODO: Check if key exists
        return data['words']


def parse_words(words):
    """
    Parses the example:
    - Determines the whole count (and therefore probabilities)
    """
    total_count = 0
    for _, weight in words.items():
        total_count += weight
    return [words, total_count]


def generate_text(words, total_length, total_count):
    text = ''
    length = 0
    while length < total_length:
        threshold = random.randint(1, total_count)
        candidate, weight = random.choice(list(words.items()))
        if weight >= threshold:
            text += candidate + '. '
            length += 1
    return text


if __name__ == '__main__':
    file_name = sys.argv[1]
    total_length = int(sys.argv[2])
    words = load_words(file_name)
    words, total_count = parse_words(words)
    text = generate_text(words, total_length, total_count)
    print(text)

