from collections import defaultdict
from wordle import format_guess
from wordle import make_guess
from wordle import ordered
from wordle import today
from wordle import word_matches
from wordle import words
import json
import string
import sys


def main(event, context):
    # handle Slack challenge
    slack_body = event.get("body")
    if slack_body is not None:
        print(f"Received Slack message: {slack_body}")
        event = json.loads(slack_body)
        typ = event.get("type")

        if typ == "url_verification":
            print("Responding to verification challenge")
            return {"statusCode": 200, "body": event["challenge"]}

        elif typ == "app_mention":
            guesses = event["text"].split()
            try:
                idx = int(guesses[0])
                guesses = guesses[1:]
                target = ordered[idx]
            except ValueError:
                target = today

            resp = guess(target, guesses)
            return {"statusCode": 200, "body": "\n".join(resp)}

    return {"statusCode": 200, "body": json.dumps("hello")}


def guess(target, guesses):
    known = [
        set(string.ascii_lowercase),
        set(string.ascii_lowercase),
        set(string.ascii_lowercase),
        set(string.ascii_lowercase),
        set(string.ascii_lowercase),
    ]

    resp = []

    reqs = defaultdict(int)

    for guess in guesses:
        make_guess(guess, target, known, reqs)

        options = {word for word in words if word_matches(word, known, reqs)}

        if 1 < len(options) < 6:
            options = sorted(options)
            suffix = f"({', '.join(format_guess(o, target, colored=False) for o in options)})"
        else:
            suffix = ""

        resp.append(
            " ".join(
                [
                    format_guess(guess, target, colored=False),
                    "=>",
                    str(len(options)),
                    "words" if len(options) != 1 else "word",
                    suffix,
                ]
            )
        )

        if guess.lower() == target.lower():
            break

    return resp
