#!/usr/bin/env python3
import argparse
import sys

from agent import DEFAULT_MODEL, run


def main():
    parser = argparse.ArgumentParser(description="Simple Claude agent with tool support")
    parser.add_argument("prompt", nargs="?", help="Prompt to send (or read from stdin)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show tool call details")
    args = parser.parse_args()

    prompt = args.prompt
    if not prompt:
        if sys.stdin.isatty():
            print("Enter prompt (Ctrl-D to submit):")
        prompt = sys.stdin.read().strip()

    if not prompt:
        parser.error("No prompt provided")

    answer = run(prompt, model=args.model, verbose=args.verbose)
    print(answer)


if __name__ == "__main__":
    main()
