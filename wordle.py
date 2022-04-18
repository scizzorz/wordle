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


def check_guess(guess: str, known: list[set[str]], reqs: dict[str, int]) -> bool:
    """Verify that a guess fits within the known information."""

    in_word = defaultdict(int)

    for guess_char in guess:
        in_word[guess_char] += 1

    for char in reqs:
        if in_word[char] < reqs[char]:
            return False

    for char, possible in zip(guess, known):
        if char not in possible:
            return False

    return True


# backwards compat
word_matches = check_guess


def find_colors(guess: str, target: str) -> (list[str], list[str], list[str]):
    """Break a guess into three arrays based on the color matches."""

    green = [""] * 5
    yellow = [""] * 5
    grey = list(guess)

    # count letter frequency.
    in_word = defaultdict(int)
    encountered = defaultdict(int)

    for target_char in target:
        in_word[target_char] += 1

    # check for greens.
    # this is a separate scan because guessing words like `PUREE` into `PURGE`
    # will incorrectly flag the first E as yellow when it's actually grey.
    for i, (guess_char, target_char) in enumerate(zip(guess, target)):
        if guess_char == target_char:
            encountered[guess_char] += 1
            green[i] = guess_char
            grey[i] = ""

    # check for yellows.
    for i, (guess_char, target_char) in enumerate(zip(guess, target)):
        # skip greens.
        if guess_char == target_char:
            continue

        encountered[guess_char] += 1
        if guess_char != target_char and encountered[guess_char] <= in_word[guess_char]:
            yellow[i] = guess_char
            grey[i] = ""

    return green, yellow, grey


def make_guess(guess: str, target: str, known: list[set[str]], reqs: dict[str, int]):
    """Make a guess against a target and add new information to the known/reqs."""

    green, yellow, grey = find_colors(guess, target)
    new_reqs = defaultdict(int)

    # check for greens.
    for i, guess_char in enumerate(green):
        if guess_char != "":
            # only allow this slot to be this guess.
            known[i] = {guess_char}
            new_reqs[guess_char] += 1

    # check for yellows.
    for i, guess_char in enumerate(yellow):
        if guess_char != "":
            # don't allow this slot to be this guess.
            known[i] -= {guess_char}
            new_reqs[guess_char] += 1

    # update the reqs dict with our new information.
    for char in new_reqs:
        if new_reqs[char] > reqs[char]:
            reqs[char] = new_reqs[char]

    # check for greys.
    for i, guess_char in enumerate(grey):
        # FIXME there's still probably a bug here.
        if guess_char == "":
            continue

        # definitely doesn't fit in this spot
        known[i] -= {guess_char}

        # but it might still fit somewhere else, so only remove it from other spots
        # if we don't require it
        if guess_char not in reqs:
            for j in range(5):
                if known[j] != {guess_char}:
                    known[j] -= {guess_char}


def format_guess(guess: str, target: str, colored: bool = True) -> str:
    """Format a guess against a target using ANSI escape codes."""

    guess = guess.upper()
    target = target.upper()

    hi_green = "\033[32m"
    hi_yellow = "\033[34m"
    hi_grey = "\033[37m"
    hi_nc = "\033[00m"

    if not colored:
        hi_green = hi_yellow = hi_grey = hi_nc = ""

    green, yellow, grey = find_colors(guess, target)
    green = [f"{hi_green}{c}" for c in green]
    yellow = [f"{hi_yellow}{c}" for c in yellow]
    grey = [f"{hi_grey}{c}" for c in grey]

    # lowercase non-options
    ret = "".join(f"{a}{b}{c}" for a, b, c in zip(green, yellow, grey)) + hi_nc

    remaining = __getattr__("ordered")
    if target.lower() in remaining:
        remaining = remaining[remaining.index(target.lower()):]

    if guess.lower() not in remaining:
        ret = ret.lower()

    return ret
