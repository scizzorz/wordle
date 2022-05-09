from collections import defaultdict
from wordle import format_guess
from wordle import make_guess
from wordle import ordered
from wordle import today
from wordle import word_matches
from wordle import words
import string
import sys

known = [
    set(string.ascii_lowercase),
    set(string.ascii_lowercase),
    set(string.ascii_lowercase),
    set(string.ascii_lowercase),
    set(string.ascii_lowercase),
]

reqs = defaultdict(int)

target, *guesses = sys.argv[1:]

try:
    target = ordered[int(target)]
except:
    pass

if target == "-":
    target = today

for guess in guesses:
    make_guess(guess, target, known, reqs)

    options = {word for word in words if word_matches(word, known, reqs)}

    if 1 < len(options) < 6:
        options = sorted(options)
        suffix = f"({', '.join(format_guess(o, target) for o in options)})"
    else:
        suffix = ""

    print(
        format_guess(guess, target),
        "=>",
        len(options),
        "words" if len(options) != 1 else "word",
        suffix
    )

    if guess.lower() == target.lower():
        break
