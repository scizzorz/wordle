from collections import defaultdict
from datetime import datetime

_words = None
_ordered = None
_remaining = None
_start = datetime(2021, 6, 19)


def __getattr__(key):
    if key in ("words", "remaining", "today", "ordered"):
        global _words
        global _remaining
        global _ordered
        if _words is None:
            with open("answer-dict") as fp:
                _ordered = [line.strip() for line in fp]

            _words = set(_ordered)

        if key == "words":
            return _words
        elif key == "remaining":
            delta = (datetime.now() - _start).days
            return _ordered[delta:]
        elif key == "ordered":
            return _ordered
        elif key == "today":
            delta = (datetime.now() - _start).days
            return _ordered[delta]


def check_guess(guess, known, reqs) -> bool:
    for r in reqs:
        if r not in guess:
            return False

    for char, poss in zip(guess, known):
        if char not in poss:
            return False

    return True


# backwards compat
word_matches = check_guess


def make_guess(guess, target, known, reqs):
    # check for greens.
    # this is a separate scan because guessing words like `PUREE` into `PURGE`
    # will incorrectly flag the first E as yellow when it's actually grey.
    green = []
    indexes = list(range(5))
    for i, guess_char, target_char in zip(indexes, guess, target):
        if guess_char == target_char:
            known[i] = {guess_char}
            green.append(i)

    guess = "".join(c for i, c in enumerate(guess) if i not in green)
    target = "".join(c for i, c in enumerate(target) if i not in green)
    indexes = [c for i, c in enumerate(indexes) if i not in green]

    # check for yellows / greys.
    for i, guess_char, target_char in zip(indexes, guess, target):
        if guess_char in target:  # yellow
            known[i] -= {guess_char}
            reqs.add(guess_char)
        else:  # grey
            # eliminate this letter from everything _except_ green squares
            for j in indexes:
                known[j] -= {guess_char}


def format_guess(guess, target):
    guess = guess.upper()
    target = target.upper()

    green = "\033[32m"
    yellow = "\033[34m"
    grey = "\033[37m"
    nc = "\033[00m"

    in_word = defaultdict(int)
    encountered = defaultdict(int)

    for target_char in target:
        in_word[target_char] += 1

    colors = [f"{grey}{guess_char}" for guess_char in guess]

    # check for greens.
    # this is a separate scan because guessing words like `PUREE` into `PURGE`
    # will incorrectly flag the first E as yellow when it's actually grey.
    for i, (guess_char, target_char) in enumerate(zip(guess, target)):
        if guess_char == target_char:
            encountered[guess_char] += 1
            colors[i] = f"{green}{guess_char}"


    # check for yellows.
    for i, (guess_char, target_char) in enumerate(zip(guess, target)):
        # skip greens.
        if guess_char == target_char:
            continue

        encountered[guess_char] += 1
        if guess_char != target_char and encountered[guess_char] <= in_word[guess_char]:
            colors[i] = f"{yellow}{guess_char}"

    # lowercase non-options
    ret = "".join(colors) + nc

    remaining = __getattr__("ordered")
    if target.lower() in remaining:
        remaining = remaining[remaining.index(target.lower()):]

    if guess.lower() not in remaining:
        ret = ret.lower()

    return ret
