from wordle import format_guess
from wordle import make_guess
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

reqs = set()

if len(sys.argv) > 1:
    target, *guesses = sys.argv[1:]
    if target == "-":
        target = today

    for guess in guesses:
        make_guess(guess, target, known, reqs)

        options = {word for word in words if word_matches(word, known, reqs)}

        suffix = f"({', '.join(sorted(options))})"
        print(
            format_guess(guess, target),
            "=>",
            len(options),
            "words" if len(options) != 1 else "word",
            suffix if 1 < len(options) < 5 else "",
        )

    sys.exit(0)

for _ in range(6):
    guess = input(" guess > ")
    result = input("result > ")
    for i, char, know in zip(range(5), guess, result):
        if know == ".":
            for j in known:
                if j != {char}:
                    j -= {char}
        elif know in string.ascii_uppercase:
            known[i] = {char}
        elif know in string.ascii_lowercase:
            known[i] -= {char}
            reqs.add(char)

    options = {word for word in words if word_matches(word, known, reqs)}
    for option in sorted(options):
        print(option)

    # print("Known:", " | ".join("".join(sorted(chars)) for chars in known))
    # print("Require:", ''.join(sorted(reqs)))
    print("Options left:", len(options))
