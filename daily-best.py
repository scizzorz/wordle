from wordle import format_guess
from wordle import make_guess
from wordle import word_matches
from wordle import remaining as words
import string
import sys


def find_options(target, *guesses):
    reqs = set()
    known = [
        set(string.ascii_lowercase),
        set(string.ascii_lowercase),
        set(string.ascii_lowercase),
        set(string.ascii_lowercase),
        set(string.ascii_lowercase),
    ]

    for guess in guesses:
        make_guess(guess, target, known, reqs)

    return {word for word in words if word_matches(word, known, reqs)}


if len(sys.argv) > 1:
    target = sys.argv[1]
else:
    from wordle import today as target

for best_score in range(1, 6):
    best_guess = set()

    for word in words:
        if word == target:
            continue

        options = find_options(target, word)

        if len(options) == best_score:
            best_guess.add(word)

    print(
        f"{best_score}: {' '.join(format_guess(g, target) for g in sorted(best_guess))}"
    )
