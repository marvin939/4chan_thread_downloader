from retriever import LinksRetriever
import unittest
import re


'''Refactor these into TestCases'''

TITLE = "       /g/ - Waiting for Ryzen thread - Technology - 4chan"
# title tag from the HTML usually has a bunch of white characters in front

REGEX_TITLE = r"\s*\/(?P<board>\w+)\/ - (?P<title>\w+(\s+\w+)*)"
title_re = re.compile(REGEX_TITLE)
matches = title_re.match(TITLE)

print("Groups:", matches.groups())

title = matches.group("title")
if title == "Waiting for Ryzen thread":
    print("Regex title matching works")
    print("Title:", title)
else:
    print("Regex title matching FAILED")

board_name = matches.group("board")
if board_name == "g":
    print("Regex board name matching works")
    print("Board:", board_name)
else:
    print("Regex board name matching FAILED")
