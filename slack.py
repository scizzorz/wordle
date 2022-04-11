from collections import defaultdict
from urllib import request
from wordle import format_guess
from wordle import make_guess
from wordle import ordered
from wordle import today
from wordle import word_matches
from wordle import words
import json
import os
import string
import sys

token = os.environ["TOKEN"].strip()


def main(event, context):
    # handle Slack challenge
    slack_body = event.get("body")
    if slack_body is not None:
        print(f"Received Slack message: {slack_body}")
        root = event = json.loads(slack_body)
        typ = event.get("type")

        if typ == "event_callback":
            print("Unpacking event callback")
            event = event["event"]
            typ = event.get("type")

        if typ == "url_verification":
            print("Responding to verification challenge")
            return {"statusCode": 200, "body": event["challenge"]}

        elif typ == "app_mention":
            print("Event text:", event["text"])
            _, *guesses = event["text"].lower().split()
            try:
                idx = int(guesses[0])
                guesses = guesses[1:]
                target = ordered[idx]
            except ValueError:
                target = today

            print(f"Guessing {guesses} against {target!r}")
            resp = guess(target, guesses)
            for line in resp:
                print(line)

            post_text = [
                "```" + "\n".join(resp) + "```",
            ]

            for g in guesses:
                if g in ordered and ordered.index(g) < ordered.index(target):
                    post_text.append(f"`{g}` was Wordle {ordered.index(g)}")

            # if channel or thread_ts don't exist we just quit (read: "die") I guess
            post = {
                "text": "\n".join(post_text),
                "channel": event["channel"],
                "thread_ts": event["thread_ts"],
            }

            json_data = json.dumps(post)
            req = request.Request(
                "https://slack.com/api/chat.postMessage",
                data=json_data.encode("ascii"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
            )

            with request.urlopen(req) as msg_resp:
                msg_resp_body = json.load(msg_resp)

            print("Slack response:", msg_resp_body)

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
