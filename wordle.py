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
    # FIXME some better logic could be done here to handle duplicate letters better

    for i, gchar, tchar, poss in zip(range(5), guess, target, known):
        if gchar == tchar:  # green
            known[i] = {gchar}
        elif gchar in target:  # yellow
            known[i] -= {gchar}
            reqs.add(gchar)
        else:  # grey
            # eliminate this letter from everything _except_ green squares
            for j in known:
                if j != {gchar}:
                    j -= {gchar}


def format_guess(guess, target):
    guess = guess.upper()
    target = target.upper()

    green = "\033[32m"
    yellow = "\033[34m"
    grey = "\033[37m"
    nc = "\033[00m"

    in_word = defaultdict(int)
    encountered = defaultdict(int)

    for tc in target:
        in_word[tc] += 1

    colors = []

    for gc, tc in zip(guess, target):
        encountered[gc] += 1
        if gc == tc:
            colors.append(f"{green}{gc}")
        elif gc != tc and encountered[gc] <= in_word[gc]:
            colors.append(f"{yellow}{gc}")
        else:
            colors.append(f"{grey}{gc}")

    # lowercase non-options
    ret = "".join(colors) + nc
    if guess.lower() not in __getattr__("remaining"):
        ret = ret.lower()

    return ret
